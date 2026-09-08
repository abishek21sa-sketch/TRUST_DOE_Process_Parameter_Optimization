"""Governed release certificates for TRUST-DOE process-development decisions.

A certificate can qualify a *shadow recipe* for engineering review. It never grants
machine write authority. The certificate hash covers the analytical evidence but not
the wall-clock timestamp, which keeps repeated evaluation of identical evidence
cryptographically stable.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def _digest(core: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(core)).hexdigest()


def build_release_certificate(
    *,
    campaign_id: str,
    release_summary: dict[str, Any],
    evidence_class: str,
    observation_count: int,
    latest_decision_hash: str | None = None,
) -> dict[str, Any]:
    recommended = dict(release_summary.get("recommended") or {})
    status = str(recommended.get("release_status", "HOLD_FOR_MORE_EVIDENCE"))
    qualified = int(release_summary.get("qualified_count", 0)) > 0 and status == "QUALIFIED_SHADOW_RECIPE"
    checks = {
        "qualified_shadow_recipe_exists": qualified,
        "production_write_blocked": release_summary.get("production_write_allowed") is False,
        "observations_available": int(observation_count) >= 8,
        "recognized_evidence_class": evidence_class in {"SYNTHETIC_VALIDATION", "EXTERNAL_VALIDATION", "PLANT_SHADOW_VALIDATION"},
    }
    decision_state = "ENGINEERING_REVIEW_REQUIRED" if all(checks.values()) else "HOLD_FOR_MORE_EVIDENCE"
    core = {
        "certificate_type": "TRUST_DOE_RELEASE_ASSURANCE_V1",
        "campaign_id": campaign_id,
        "decision_state": decision_state,
        "recommended_shadow_recipe": recommended,
        "frontier_counts": {
            "candidate_count": int(release_summary.get("candidate_count", 0)),
            "pareto_count": int(release_summary.get("pareto_count", 0)),
            "qualified_count": int(release_summary.get("qualified_count", 0)),
        },
        "evidence_class": evidence_class,
        "observation_count": int(observation_count),
        "checks": checks,
        "approval_authority": "PROCESS_DEVELOPMENT_ENGINEER",
        "secondary_review": "QUALITY_OR_MANUFACTURING_ENGINEER",
        "production_write_allowed": False,
        "latest_decision_hash": latest_decision_hash,
        "claim_boundary": "Qualification is for governed shadow experimentation only; it is not production recipe authorization or realized plant performance evidence.",
    }
    return {
        **core,
        "certificate_sha256": _digest(core),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def verify_release_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    stored = certificate.get("certificate_sha256")
    core = {k: v for k, v in certificate.items() if k not in {"certificate_sha256", "generated_at_utc"}}
    expected = _digest(core)
    return {
        "valid": bool(stored and stored == expected),
        "stored_sha256": stored,
        "expected_sha256": expected,
        "decision_state": certificate.get("decision_state"),
        "production_write_allowed": certificate.get("production_write_allowed"),
    }
