"""Portfolio-grade validation and decision-certificate construction for TRUST-DOE.

This module intentionally does not authorize machine writes. It converts the core
scientific engines into an auditable release artifact: strategy race, robust recipe,
perturbation stress, and an explicit qualification state with reasons.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .or_engine import optimize_robust_recipe
from .process import SyntheticAMOracle
from .race import experiment_race
from .robustness import stress_recipe


def build_portfolio_certificate(*, seed: int = 2026, race_budget: int = 4) -> dict:
    oracle = SyntheticAMOracle(seed=seed)
    robust = optimize_robust_recipe(
        oracle,
        seed=seed,
        n_scenarios=80,
        min_feasibility=0.95,
        risk_weight=0.35,
    )
    stress = stress_recipe(oracle, robust.recipe, relative_sigma=0.015, n=1000, seed=seed + 1)
    race = experiment_race(budget=race_budget, seed=seed)
    by_name = {r.strategy: r for r in race}
    trust = by_name["TRUST-DOE-S"]
    unsafe_min = min(r.unsafe_trials for r in race)

    qualification_reasons: list[str] = []
    if robust.status != "ROBUST_FEASIBLE":
        qualification_reasons.append("robust recipe failed scenario feasibility gate")
    if stress.feasibility_probability < 0.95:
        qualification_reasons.append("local perturbation feasibility probability below 0.95")
    if trust.unsafe_trials > unsafe_min:
        qualification_reasons.append("TRUST-DOE-S did not achieve the minimum unsafe-trial count in the benchmark")

    state = "SHADOW_TRIAL_READY" if not qualification_reasons else "HOLD"
    core = {
        "release": "TRUST-DOE_PORTFOLIO_RELEASE",
        "evidence_boundary": "Synthetic additive-manufacturing benchmark; no plant-performance or production-control claim.",
        "seed": seed,
        "race_budget": race_budget,
        "robust_recipe": asdict(robust),
        "perturbation_stress": asdict(stress),
        "strategy_race": [asdict(r) for r in race],
        "qualification": {
            "state": state,
            "reasons": qualification_reasons,
            "production_write_allowed": False,
            "required_human_action": "Review evidence and authorize a governed shadow trial; production machine write remains blocked.",
        },
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    digest_payload = dict(core)
    digest_payload.pop("generated_at_utc")
    core["evidence_hash"] = hashlib.sha256(
        json.dumps(digest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return core


def write_portfolio_certificate(path: str | Path, *, seed: int = 2026, race_budget: int = 4) -> dict:
    payload = build_portfolio_certificate(seed=seed, race_budget=race_budget)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload
