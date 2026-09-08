from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
import numpy as np
from .process import SyntheticAMOracle
from .campaign import run_closed_loop
from .race import experiment_race, race_payload
from .ablation import acquisition_ablation, ablation_payload
from .release import build_release_frontier, release_summary
from .calibration import cross_validated_conformal


def _surface_payload(oracle: SyntheticAMOracle, recipe: np.ndarray, n: int = 33) -> dict:
    powers = np.linspace(oracle.space.factors[0].low, oracle.space.factors[0].high, n)
    speeds = np.linspace(oracle.space.factors[1].low, oracle.space.factors[1].high, n)
    objective = []
    safety = []
    for speed in speeds:
        obj_row, safe_row = [], []
        for power in powers:
            x = recipe.copy()
            x[0], x[1] = power, speed
            o, s = oracle.noiseless(x)
            obj_row.append(o)
            safe_row.append(s)
        objective.append(obj_row)
        safety.append(safe_row)
    return {
        "x_factor": oracle.space.factors[0].name,
        "x_unit": oracle.space.factors[0].unit,
        "x": powers.tolist(),
        "y_factor": oracle.space.factors[1].name,
        "y_unit": oracle.space.factors[1].unit,
        "y": speeds.tolist(),
        "objective": objective,
        "safety": safety,
        "fixed_recipe": recipe.tolist(),
    }


def build_phaseb_evidence(root: str | Path = ".", seed: int = 2026, quick: bool = False) -> dict:
    root = Path(root)
    oracle = SyntheticAMOracle(seed=seed)
    campaign = run_closed_loop(oracle, budget=2 if quick else 8, seed=seed)
    incumbent = campaign.state.incumbent()
    race = experiment_race(budget=1 if quick else 6, seed=seed)
    ablation = [] if quick else acquisition_ablation(seed=seed + 71)
    frontier = build_release_frontier(campaign.state, oracle.space, oracle, n_candidates=12 if quick else 64, stress_samples=60 if quick else 450, seed=seed + 81)
    release = release_summary(frontier)
    cal_obj = cross_validated_conformal(oracle.space, campaign.state.observations, "objective", 0.90, seed=seed + 91)
    cal_safe = cross_validated_conformal(oracle.space, campaign.state.observations, "safety_margin", 0.90, seed=seed + 92)
    payload = {
        "version": "0.7.0",
        "phase": "B",
        "evidence_class": "SYNTHETIC_VALIDATION",
        "signature_capability": "SAFE_EXPERIMENT_COCKPIT",
        "signature_algorithm": "TRUST-DOE-S",
        "production_write_allowed": False,
        "process_space": [asdict(f) for f in oracle.space.factors],
        "campaign": {
            "iterations": campaign.state.iteration,
            "trust_radius": campaign.state.trust_radius,
            "incumbent": asdict(incumbent),
            "steps": [{
                "iteration": s.iteration,
                "decision": asdict(s.decision),
                "observation": asdict(s.observation),
                "trust_radius_after": s.trust_radius_after,
            } for s in campaign.steps],
        },
        "calibration": {
            "objective": asdict(cal_obj),
            "safety": asdict(cal_safe),
        },
        "experiment_race": race_payload(race),
        "acquisition_ablation": ablation_payload(ablation),
        "release": release,
        "release_frontier": [asdict(x) for x in frontier],
        "surface": _surface_payload(oracle, np.asarray(incumbent.recipe)),
        "governance": {
            "mode": "SHADOW_EXPERIMENT_ONLY",
            "autonomous_machine_write": False,
            "external_validation_status": "PENDING",
            "release_claim": "Portfolio engineering validation on a deterministic synthetic benchmark; not factory validation.",
        },
    }
    artifacts = root / "artifacts"
    workbench = root / "workbench"
    artifacts.mkdir(parents=True, exist_ok=True)
    workbench.mkdir(parents=True, exist_ok=True)
    (artifacts / "phaseB_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (workbench / "data.json").write_text(json.dumps(payload), encoding="utf-8")
    return payload
