from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from .process import SyntheticAMOracle
from .campaign import initialize_campaign
from .acquisition import AcquisitionConfig, optimize_next_experiment


@dataclass(frozen=True)
class AblationResult:
    label: str
    lambda_improvement: float
    lambda_information: float
    distance_penalty: float
    predicted_objective: float
    conservative_objective_halfwidth: float
    conservative_safety_margin: float
    information_gain: float
    normalized_distance: float
    score: float
    production_write_allowed: bool = False


def acquisition_ablation(seed: int = 42) -> list[AblationResult]:
    oracle = SyntheticAMOracle(seed=seed)
    state = initialize_campaign(oracle, n_initial=18, seed=seed)
    configs = [
        ("EXPLOIT", 1.6, 0.04, 0.03),
        ("BALANCED", 1.0, 0.18, 0.04),
        ("LEARN", 0.35, 0.48, 0.025),
        ("LOCAL-CONSERVATIVE", 1.0, 0.12, 0.16),
    ]
    out = []
    for i, (label, li, lg, dp) in enumerate(configs):
        cfg = AcquisitionConfig(lambda_improvement=li, lambda_information=lg, distance_penalty=dp, optimizer_maxiter=28, population_size=8)
        dec, _ = optimize_next_experiment(state, oracle.space, cfg, seed=seed + 200 + i)
        out.append(AblationResult(
            label, li, lg, dp, dec.predicted_objective, dec.objective_std,
            dec.predicted_safety - dec.safety_std, dec.information_gain,
            dec.normalized_distance, dec.score, False
        ))
    return out


def ablation_payload(rows: list[AblationResult]) -> list[dict]:
    return [asdict(r) for r in rows]
