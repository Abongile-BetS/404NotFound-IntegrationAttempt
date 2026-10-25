from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.entities import Alert, Customer, FeatureSnapshot, RiskAssessment, Rule, RuleExecution, Transaction, KycRecord, ScreeningJob


DEFAULT_RULES = [
    ("TXN_SPIKE", "Deposit spike", "transaction", "high", 18, {"minimum_total": 25000, "minimum_count": 3}),
    ("TXN_VELOCITY", "High-frequency deposits", "transaction", "medium", 12, {"minimum_count": 8}),
    ("LOW_WAGER_WITHDRAW", "Minimal wagering before withdrawal", "behaviour", "high", 20, {"ratio_below": 0.2, "minimum_withdrawal": 1000, "minimum_deposit": 1000}),
    ("KYC_INCOMPLETE", "Incomplete customer due diligence", "kyc", "medium", 10, {}),
]


def seed_rules(db: Session) -> None:
    for code, name, category, severity, points, config in DEFAULT_RULES:
        if not db.scalar(select(Rule).where(Rule.code == code, Rule.version == 1)):
            db.add(Rule(code=code, name=name, category=category, severity=severity, risk_points=points, config=config, approved=True))
    db.commit()


def _totals(db: Session, customer_id: str, start: datetime, end: datetime) -> dict:
    rows = db.execute(select(Transaction.kind, func.count(), func.coalesce(func.sum(Transaction.amount), 0), func.coalesce(func.max(Transaction.amount), 0)).where(Transaction.customer_id == customer_id, Transaction.occurred_at >= start, Transaction.occurred_at < end).group_by(Transaction.kind)).all()
    return {str(kind).lower(): {"count": int(count), "amount": float(total), "maximum": float(maximum)} for kind, count, total, maximum in rows}


def calculate_features(db: Session, customer_id: str, *, as_of: datetime | None = None, persist: bool = True) -> dict:
    """Shared point-in-time features for deterministic AML rules and future ML.

    A fixed as_of timestamp avoids look-ahead leakage in historical backtests.
    Transaction.kind='bet' represents settled wagering turnover in the current schema.
    """
    now = as_of or datetime.now(timezone.utc)
    features: dict = {}
    for days in (1, 7, 30, 90):
        window = _totals(db, customer_id, now - timedelta(days=days), now)
        features[f"{days}d"] = window
        if persist:
            db.add(FeatureSnapshot(customer_id=customer_id, window=f"{days}d", features=window, quality={"complete": True, "as_of": now.isoformat(), "source": "transactions"}))
    previous = _totals(db, customer_id, now - timedelta(days=60), now - timedelta(days=30))
    current = features["30d"].get("deposit", {}).get("amount", 0)
    baseline = previous.get("deposit", {}).get("amount", 0)
    dep7 = features["7d"].get("deposit", {}).get("amount", 0)
    withdrawal7 = features["7d"].get("withdrawal", {}).get("amount", 0)
    bet7 = features["7d"].get("bet", {}).get("amount", 0)
    features["derived"] = {
        "deposit_previous_30d": baseline,
        "deposit_growth_pct": round((current - baseline) / baseline * 100, 2) if baseline > 0 else None,
        "deposit_growth_baseline_available": baseline > 0,
        "withdrawal_to_deposit_ratio_7d": round(withdrawal7 / dep7, 4) if dep7 > 0 else None,
        "wagering_to_deposit_ratio_7d": round(bet7 / dep7, 4) if dep7 > 0 else None,
        "as_of": now.isoformat(),
    }
    if persist:
        db.flush()
    return features


def evaluate_rule(code: str, config: dict, features: dict, customer: Customer) -> tuple[bool, dict, str]:
    """Return (triggered, evidence, execution_status). Missing data is never a pass."""
    seven = features["7d"]
    dep = seven.get("deposit", {"count": 0, "amount": 0})
    wd = seven.get("withdrawal", {"count": 0, "amount": 0})
    bet = seven.get("bet", {"count": 0, "amount": 0})
    derived = features["derived"]
    if code == "TXN_SPIKE":
        threshold = {"minimum_total": float(config.get("minimum_total", 25000)), "minimum_count": int(config.get("minimum_count", 3))}
        observed = {"deposit_total_7d": dep["amount"], "deposit_count_7d": dep["count"]}
        return dep["amount"] >= threshold["minimum_total"] and dep["count"] >= threshold["minimum_count"], {"observed": observed, "threshold": threshold}, "evaluated"
    if code == "TXN_VELOCITY":
        threshold = {"minimum_count": int(config.get("minimum_count", 8))}
        return dep["count"] >= threshold["minimum_count"], {"observed": {"deposit_count_7d": dep["count"]}, "threshold": threshold}, "evaluated"
    if code == "LOW_WAGER_WITHDRAW":
        threshold = {"ratio_below": float(config.get("ratio_below", 0.2)), "minimum_deposit": float(config.get("minimum_deposit", 1000)), "minimum_withdrawal": float(config.get("minimum_withdrawal", 1000))}
        evidence = {"observed": {"deposit_total_7d": dep["amount"], "withdrawal_total_7d": wd["amount"], "wagering_total_7d": bet["amount"], "wagering_to_deposit_ratio": derived["wagering_to_deposit_ratio_7d"]}, "threshold": threshold}
        if not bet["count"] and not bet["amount"]:
            return False, {**evidence, "reason": "No wagering records: cannot distinguish zero wagering from missing feed"}, "unavailable"
        ratio = derived["wagering_to_deposit_ratio_7d"]
        return dep["amount"] >= threshold["minimum_deposit"] and wd["amount"] >= threshold["minimum_withdrawal"] and ratio is not None and ratio < threshold["ratio_below"], evidence, "evaluated"
    if code == "KYC_INCOMPLETE":
        accepted = config.get("accepted_statuses", ["verified", "approved"])
        return customer.kyc_status not in accepted, {"observed": {"kyc_status": customer.kyc_status}, "threshold": {"accepted_statuses": accepted}}, "evaluated"
    return False, {"reason": "No registered evaluator for rule"}, "unavailable"


def assess_customer(db: Session, customer: Customer) -> RiskAssessment:
    features = calculate_features(db, customer.id)
    score, drivers, unavailable = 0, [], []
    rules = db.scalars(select(Rule).where(Rule.enabled.is_(True), Rule.approved.is_(True)).order_by(Rule.code, Rule.version.desc())).all()
    evaluated_codes = set()
    for rule in rules:
        if rule.code in evaluated_codes:
            continue  # only newest approved active version of each rule
        evaluated_codes.add(rule.code)
        triggered, evidence, status = evaluate_rule(rule.code, rule.config or {}, features, customer)
        evidence = {"window": "7d", "execution_status": status, "rule_version": rule.version, **evidence}
        contribution = rule.risk_points if triggered and status == "evaluated" else 0
        explanation = f"{rule.name}: {status}; {'triggered' if triggered else 'not triggered'}."
        db.add(RuleExecution(rule_id=rule.id, customer_id=customer.id, triggered=triggered, inputs={"features_7d": features["7d"], "derived": features["derived"], "kyc_status": customer.kyc_status}, evidence=evidence, explanation=explanation, score_contribution=contribution))
        if status != "evaluated":
            unavailable.append(rule.code)
        if contribution:
            score += contribution
            drivers.append({"rule": rule.code, "name": rule.name, "version": rule.version, "explanation": explanation, "points": contribution, "evidence": evidence, "recommended_action": "Review retained evidence before taking action."})
    score = min(score, 100)
    level = "critical" if score >= 75 else "high" if score >= 45 else "medium" if score >= 25 else "low"
    coverage = (len(evaluated_codes) - len(unavailable)) / len(evaluated_codes) if evaluated_codes else 0
    assessment = RiskAssessment(customer_id=customer.id, score=score, level=level, components={"rules": score, "ml": 0, "screening": 0, "coverage": round(coverage, 3), "unavailable_rules": unavailable, "assessment_status": "complete" if not unavailable else "partial"}, drivers=drivers, model_version="risk-v2-configured", confidence=Decimal(str(round(coverage, 3))))
    db.add(assessment)
    customer.risk_score, customer.risk_level = score, level
    if score >= 25:
        existing = db.scalar(select(Alert).where(Alert.customer_id == customer.id, Alert.status.in_(["open", "acknowledged"]), Alert.title == "AML risk reassessment"))
        if not existing:
            db.add(Alert(customer_id=customer.id, title="AML risk reassessment", severity=level, evidence={"assessment_id": assessment.id, "drivers": drivers, "coverage": coverage, "recommended_action": "Review AML/KYC evidence and unresolved data gaps."}))
    db.commit()
    db.refresh(assessment)
    return assessment
