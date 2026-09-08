from copy import deepcopy
from trustdoe.governance import build_release_certificate, verify_release_certificate


def summary(status="QUALIFIED_SHADOW_RECIPE"):
    return {
        "candidate_count": 18,
        "pareto_count": 4,
        "qualified_count": 2 if status == "QUALIFIED_SHADOW_RECIPE" else 0,
        "recommended": {
            "recipe": [230.0, 980.0, 0.10, 0.04],
            "feasibility_probability": 0.995,
            "conservative_safety_margin": 0.08,
            "robust_p95_objective": 0.22,
            "release_status": status,
            "production_write_allowed": False,
        },
        "production_write_allowed": False,
        "evidence_class": "SYNTHETIC_VALIDATION",
    }


def test_release_certificate_requires_human_review_and_blocks_machine_write():
    c = build_release_certificate(campaign_id="CMP-1", release_summary=summary(), evidence_class="SYNTHETIC_VALIDATION", observation_count=14)
    assert c["decision_state"] == "ENGINEERING_REVIEW_REQUIRED"
    assert c["production_write_allowed"] is False
    assert verify_release_certificate(c)["valid"] is True


def test_release_certificate_tamper_detection_and_hold_state():
    c = build_release_certificate(campaign_id="CMP-2", release_summary=summary("HOLD_FOR_MORE_EVIDENCE"), evidence_class="SYNTHETIC_VALIDATION", observation_count=14)
    assert c["decision_state"] == "HOLD_FOR_MORE_EVIDENCE"
    bad = deepcopy(c)
    bad["recommended_shadow_recipe"]["feasibility_probability"] = 1.0
    assert verify_release_certificate(bad)["valid"] is False
