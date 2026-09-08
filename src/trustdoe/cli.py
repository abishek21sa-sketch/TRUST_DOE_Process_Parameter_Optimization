from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
import numpy as np
from .process import SyntheticAMOracle
from .campaign import run_closed_loop
from .benchmark import compare_strategies
from .robustness import stress_recipe


def main():
    oracle = SyntheticAMOracle(seed=17)
    result = run_closed_loop(oracle, budget=8, seed=2026)
    incumbent = result.state.incumbent()
    robust = stress_recipe(oracle, np.array(incumbent.recipe), n=2500, seed=99)
    bench = compare_strategies(budget=8, seed=2026)
    payload = {
        "evidence_class": "SYNTHETIC_VALIDATION",
        "signature_algorithm": "TRUST-DOE-S",
        "production_write_allowed": False,
        "iterations": result.state.iteration,
        "final_trust_radius": result.state.trust_radius,
        "incumbent": asdict(incumbent),
        "robustness": asdict(robust),
        "benchmark": [asdict(x) for x in bench],
        "steps": [
            {
                "iteration": s.iteration,
                "recipe": s.decision.recipe,
                "predicted_objective": s.decision.predicted_objective,
                "objective_std": s.decision.objective_std,
                "information_gain": s.decision.information_gain,
                "score": s.decision.score,
                "observed_objective": s.observation.objective,
                "observed_safety_margin": s.observation.safety_margin,
                "trust_radius_after": s.trust_radius_after,
                "production_write_allowed": s.decision.production_write_allowed,
            } for s in result.steps
        ]
    }
    out = Path("artifacts")
    out.mkdir(exist_ok=True)
    (out/"phaseA_campaign.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k != "steps"}, indent=2))
    print("PHASE A CLOSED-LOOP DIAGNOSTIC: PASS")

if __name__ == "__main__":
    main()
