from trustdoe.portfolio_validation import build_portfolio_certificate


def test_portfolio_certificate_is_governed_and_reproducible_on_scientific_payload():
    a = build_portfolio_certificate(seed=404, race_budget=1)
    b = build_portfolio_certificate(seed=404, race_budget=1)
    assert a["release"] == "TRUST-DOE_PORTFOLIO_RC1"
    assert a["qualification"]["production_write_allowed"] is False
    assert a["qualification"]["state"] in {"SHADOW_TRIAL_READY", "HOLD"}
    assert a["evidence_hash"] == b["evidence_hash"]
    assert {r["strategy"] for r in a["strategy_race"]} == {
        "TRUST-DOE-S", "RANDOM-LHS", "STATIC-DOE", "UNCONSTRAINED-BO"
    }
