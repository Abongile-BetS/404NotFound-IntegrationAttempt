"""Additive, deterministic AML rules. No writes to the host platform's tables."""

import math
from datetime import UTC, datetime, timedelta
from typing import Any

RULES = [
    ("AML-TXN-001", "Seven-day withdrawal/deposit ratio", "transaction", 15),
    ("AML-TXN-002", "Deposit activity spike", "transaction", 12),
    ("AML-TXN-003", "High deposit frequency", "transaction", 8),
    ("AML-TXN-004", "Unusual withdrawal frequency", "transaction", 8),
    ("AML-BHV-001", "Dormant-to-active behaviour", "behaviour", 12),
    ("AML-BHV-002", "Large average deposit", "behaviour", 8),
    ("AML-KYC-001", "CDD incomplete", "kyc", 12),
    ("AML-SCR-001", "Potential sanctions screening hit", "screening", 20),
    ("AML-SCR-002", "Potential PEP screening hit", "screening", 12),
    ("AML-MED-001", "Potential adverse media hit", "media", 12),
    ("AML-NET-001", "Shared device relationships", "network", 10),
    ("AML-GEO-001", "Customer geographic profile missing", "geography", 5),
]
THRESHOLDS = {
    "AML-TXN-001": {"min_deposit": 10000, "min_withdrawal": 10000, "min_ratio": 0.8},
    "AML-TXN-002": {"min_previous": 1000, "min_growth_pct": 150},
    "AML-TXN-003": {"min_count": 10},
    "AML-TXN-004": {"min_count": 8},
    "AML-BHV-001": {"dormant_days": 60, "min_recent_deposit": 10000},
    "AML-BHV-002": {"min_average": 10000},
    "AML-NET-001": {"min_links": 2},
}


def features(transactions: list[dict], as_of: datetime | None = None) -> dict[str, Any]:
    now = as_of or datetime.now(UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    def parse(t):
        v = t.get("transaction_timestamp") or t.get("timestamp")
        if isinstance(v, datetime):
            d = v
        elif isinstance(v, str):
            try:
                d = datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                return None
        else:
            return None
        return d.replace(tzinfo=UTC) if d.tzinfo is None else d.astimezone(UTC)

    rows = []
    for t in transactions:
        dt = parse(t)
        if dt is None or dt > now:
            continue
        try:
            amount = float(t.get("transaction_amount", t.get("amount", 0)))
        except (TypeError, ValueError):
            continue
        if amount < 0 or not math.isfinite(amount):
            continue
        kind = str(t.get("transaction_type", "")).strip().upper()
        rows.append((dt, kind, amount))

    def totals(kind, start, end):
        values = [a for d, k, a in rows if k == kind and start <= d < end]
        return round(sum(values), 2), len(values)

    dep7, dc7 = totals(
        "DEPOSIT", now - timedelta(days=7), now + timedelta(microseconds=1)
    )
    wd7, wc7 = totals(
        "WITHDRAWAL", now - timedelta(days=7), now + timedelta(microseconds=1)
    )
    dep30, dc30 = totals(
        "DEPOSIT", now - timedelta(days=30), now + timedelta(microseconds=1)
    )
    prev30, _ = totals("DEPOSIT", now - timedelta(days=60), now - timedelta(days=30))
    historical = [
        d for d, k, a in rows if k == "DEPOSIT" and d < now - timedelta(days=30)
    ]
    return {
        "deposit_7d": dep7,
        "withdrawal_7d": wd7,
        "deposit_count_7d": dc7,
        "withdrawal_count_7d": wc7,
        "deposit_30d": dep30,
        "deposit_count_30d": dc30,
        "deposit_prev_30d": prev30,
        "deposit_growth_pct": round((dep30 - prev30) / prev30 * 100, 2)
        if prev30 > 0
        else None,
        "withdrawal_deposit_ratio_7d": round(wd7 / dep7, 4) if dep7 > 0 else None,
        "average_deposit_30d": round(dep30 / dc30, 2) if dc30 else None,
        "days_since_prior_deposit": (now - max(historical)).days
        if historical
        else None,
        "transaction_rows": len(rows),
        "as_of": now.isoformat(),
    }


def evaluate(
    f: dict, customer: dict, screenings: list[dict], network_links: int | None = None
) -> dict:
    findings = []
    checks = {}

    def check(code, trigger, evidence=None, available=True):
        checks[code] = {
            "status": "TRIGGERED"
            if trigger
            else ("CLEAR" if available else "UNAVAILABLE"),
            "evidence": evidence or {},
        }
        if trigger:
            spec = next(x for x in RULES if x[0] == code)
            findings.append(
                {
                    "rule_code": code,
                    "name": spec[1],
                    "category": spec[2],
                    "points": spec[3],
                    "evidence": evidence or {},
                }
            )

    r = f["withdrawal_deposit_ratio_7d"]
    t = THRESHOLDS["AML-TXN-001"]
    check(
        "AML-TXN-001",
        r is not None
        and f["deposit_7d"] >= t["min_deposit"]
        and f["withdrawal_7d"] >= t["min_withdrawal"]
        and r >= t["min_ratio"],
        {"ratio": r, "deposit": f["deposit_7d"], "withdrawal": f["withdrawal_7d"]},
        f["transaction_rows"] > 0,
    )
    growth = f["deposit_growth_pct"]
    t = THRESHOLDS["AML-TXN-002"]
    check(
        "AML-TXN-002",
        growth is not None
        and f["deposit_prev_30d"] >= t["min_previous"]
        and growth >= t["min_growth_pct"],
        {"growth_pct": growth},
        growth is not None,
    )
    t = THRESHOLDS["AML-TXN-003"]
    check(
        "AML-TXN-003",
        f["deposit_count_7d"] >= t["min_count"],
        {"count": f["deposit_count_7d"], "threshold": t["min_count"]},
        f["transaction_rows"] > 0,
    )
    t = THRESHOLDS["AML-TXN-004"]
    check(
        "AML-TXN-004",
        f["withdrawal_count_7d"] >= t["min_count"],
        {"count": f["withdrawal_count_7d"], "threshold": t["min_count"]},
        f["transaction_rows"] > 0,
    )
    dormant = f["days_since_prior_deposit"]
    t = THRESHOLDS["AML-BHV-001"]
    check(
        "AML-BHV-001",
        dormant is not None
        and dormant >= t["dormant_days"]
        and f["deposit_30d"] >= t["min_recent_deposit"],
        {
            "dormant_days": dormant,
            "recent_deposit_30d": f["deposit_30d"],
            "thresholds": t,
        },
        dormant is not None,
    )
    avg = f["average_deposit_30d"]
    t = THRESHOLDS["AML-BHV-002"]
    check(
        "AML-BHV-002",
        avg is not None and avg >= t["min_average"],
        {"average": avg, "threshold": t["min_average"]},
        avg is not None,
    )
    fica = customer.get("customer_fica_compliant")
    check("AML-KYC-001", fica is False, {"fica_compliant": fica}, fica is not None)
    for code, typ in [
        ("AML-SCR-001", "sanction"),
        ("AML-SCR-002", "pep"),
        ("AML-MED-001", "media"),
    ]:
        matching = [
            s for s in screenings if typ in str(s.get("screening_type", "")).lower()
        ]
        hits = [
            s
            for s in matching
            if s.get("match_found") is True
            or str(s.get("result", "")).upper()
            in ("MATCH", "POTENTIAL_MATCH", "REVIEW_REQUIRED")
        ]
        check(
            code,
            bool(hits),
            {"matching_records": len(matching), "candidate_hits": len(hits)},
            bool(matching),
        )
    check(
        "AML-NET-001",
        network_links is not None
        and network_links >= THRESHOLDS["AML-NET-001"]["min_links"],
        {"linked_customers": network_links},
        network_links is not None,
    )
    country = customer.get("country")
    check(
        "AML-GEO-001",
        not bool(country and str(country).strip()),
        {"country_present": bool(country)},
        True,
    )
    points = sum(x["points"] for x in findings)
    unavailable = [k for k, v in checks.items() if v["status"] == "UNAVAILABLE"]
    score = min(100, points)
    return {
        "score": score,
        "risk_level": "CRITICAL"
        if score >= 75
        else "HIGH"
        if score >= 50
        else "MEDIUM"
        if score >= 25
        else "LOW",
        "assessment_status": "INCOMPLETE" if unavailable else "COMPLETE",
        "unavailable_rules": unavailable,
        "findings": findings,
        "rules": checks,
        "model_version": "enterprise-extension-1.0",
        "note": "Illustrative deterministic rule score; not an approved compliance risk rating. Screening candidate hits require analyst confirmation.",
    }
