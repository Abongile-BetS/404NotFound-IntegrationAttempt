from types import SimpleNamespace
from app.services.risk import evaluate_rule


def fixture_features(bet_count=2, bet_amount=100):
    return {"7d": {"deposit": {"count": 4, "amount": 30000}, "withdrawal": {"count": 1, "amount": 25000}, "bet": {"count": bet_count, "amount": bet_amount}}, "derived": {"wagering_to_deposit_ratio_7d": bet_amount / 30000 if bet_count else 0}}


def test_configured_threshold_is_applied():
    customer = SimpleNamespace(kyc_status="verified")
    assert evaluate_rule("TXN_SPIKE", {"minimum_total": 40000, "minimum_count": 3}, fixture_features(), customer)[0] is False
    assert evaluate_rule("TXN_SPIKE", {"minimum_total": 20000, "minimum_count": 3}, fixture_features(), customer)[0] is True


def test_low_wagering_uses_betting_not_withdrawal_ratio():
    customer = SimpleNamespace(kyc_status="verified")
    triggered, evidence, status = evaluate_rule("LOW_WAGER_WITHDRAW", {"ratio_below": 0.2}, fixture_features(), customer)
    assert (triggered, status) == (True, "evaluated")
    assert evidence["observed"]["wagering_total_7d"] == 100


def test_absent_betting_feed_is_not_clean_result():
    customer = SimpleNamespace(kyc_status="verified")
    assert evaluate_rule("LOW_WAGER_WITHDRAW", {}, fixture_features(0, 0), customer)[2] == "unavailable"


def test_incomplete_kyc():
    assert evaluate_rule("KYC_INCOMPLETE", {}, fixture_features(), SimpleNamespace(kyc_status="pending"))[0]
