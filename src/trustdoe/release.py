from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from .domain import CampaignState, ProcessSpace
from .process import SyntheticAMOracle
from .surrogate import GPSurrogate
from .calibration import cross_validated_conformal
from .robustness import stress_recipe
from .doe import latin_hypercube


@dataclass(frozen=True)
class ReleaseCandidate:
    recipe: tuple[float, ...]
    predicted_objective: float
    objective_upper: float
    conservative_safety_margin: float
    robust_expected_objective: float
    robust_p95_objective: float
    feasibility_probability: float
    distance_from_incumbent: float
    pareto_efficient: bool
    release_status: str
    production_write_allowed: bool = False


@dataclass(frozen=True)
class ReleasePolicy:
    min_feasibility_probability: float = 0.99
    min_conservative_safety_margin: float = 0.02
    max_relative_p95_degradation: float = 1.20
    calibration_coverage: float = 0.90


def _pareto_mask(rows: list[dict]) -> np.ndarray:
    # minimize expected and p95 objective, maximize feasibility probability and safety margin
    vals = np.array([[r["robust_expected_objective"], r["robust_p95_objective"], -r["feasibility_probability"], -r["conservative_safety_margin"]] for r in rows])
    mask = np.ones(len(vals), dtype=bool)
    for i, v in enumerate(vals):
        dominated = np.any(np.all(vals <= v + 1e-12, axis=1) & np.any(vals < v - 1e-12, axis=1))
        mask[i] = not dominated
    return mask


def build_release_frontier(
    state: CampaignState,
    space: ProcessSpace,
    oracle: SyntheticAMOracle,
    n_candidates: int = 96,
    stress_samples: int = 650,
    seed: int = 818,
    policy: ReleasePolicy = ReleasePolicy(),
) -> list[ReleaseCandidate]:
    incumbent = state.incumbent()
    center_z = space.normalize(incumbent.recipe)
    obj_gp = GPSurrogate(space, seed=seed).fit(state.observations, "objective")
    safe_gp = GPSurrogate(space, seed=seed + 1).fit(state.observations, "safety_margin")
    obj_cal = cross_validated_conformal(space, state.observations, "objective", policy.calibration_coverage, seed=seed + 2)
    safe_cal = cross_validated_conformal(space, state.observations, "safety_margin", policy.calibration_coverage, seed=seed + 3)

    global_design = latin_hypercube(space, n_candidates, seed=seed + 10)
    rng = np.random.default_rng(seed + 11)
    local_z = np.clip(center_z + rng.normal(0.0, max(0.05, state.trust_radius / 2.8), size=(n_candidates, space.dimension)), -1, 1)
    local_design = np.array([space.denormalize(z) for z in local_z])
    designs = np.vstack([np.array([incumbent.recipe]), global_design, local_design])

    obj = obj_gp.predict(designs)
    safe = safe_gp.predict(designs)
    rows: list[dict] = []
    incumbent_robust = stress_recipe(oracle, np.asarray(incumbent.recipe), n=stress_samples, seed=seed + 99)
    p95_limit = max(incumbent_robust.objective_p95 * policy.max_relative_p95_degradation, incumbent_robust.objective_p95 + 0.02)

    for i, recipe in enumerate(designs):
        dist = float(np.linalg.norm(space.normalize(recipe) - center_z))
        if dist > max(state.trust_radius, 0.25) + 1e-12:
            continue
        obj_hw = max(1.64 * float(obj.std[i]), obj_cal.absolute_error_quantile)
        safe_hw = max(1.64 * float(safe.std[i]), safe_cal.absolute_error_quantile)
        conservative_safety = float(safe.mean[i] - safe_hw)
        robust = stress_recipe(oracle, recipe, n=stress_samples, seed=seed + 1000 + i)
        qualified = (
            conservative_safety >= policy.min_conservative_safety_margin
            and robust.feasibility_probability >= policy.min_feasibility_probability
            and robust.objective_p95 <= p95_limit
        )
        rows.append({
            "recipe": tuple(map(float, recipe)),
            "predicted_objective": float(obj.mean[i]),
            "objective_upper": float(obj.mean[i] + obj_hw),
            "conservative_safety_margin": conservative_safety,
            "robust_expected_objective": robust.expected_objective,
            "robust_p95_objective": robust.objective_p95,
            "feasibility_probability": robust.feasibility_probability,
            "distance_from_incumbent": dist,
            "pareto_efficient": False,
            "release_status": "QUALIFIED_SHADOW_RECIPE" if qualified else "HOLD_FOR_MORE_EVIDENCE",
            "production_write_allowed": False,
        })
    if not rows:
        raise RuntimeError("No release candidates within governed trust region")
    mask = _pareto_mask(rows)
    for r, efficient in zip(rows, mask):
        r["pareto_efficient"] = bool(efficient)
    return [ReleaseCandidate(**r) for r in rows]


def release_summary(frontier: list[ReleaseCandidate]) -> dict:
    qualified = [r for r in frontier if r.release_status == "QUALIFIED_SHADOW_RECIPE"]
    pareto = [r for r in frontier if r.pareto_efficient]
    best = min(qualified or pareto or frontier, key=lambda r: (r.robust_expected_objective, r.robust_p95_objective))
    return {
        "candidate_count": len(frontier),
        "pareto_count": len(pareto),
        "qualified_count": len(qualified),
        "recommended": asdict(best),
        "production_write_allowed": False,
        "evidence_class": "SYNTHETIC_VALIDATION",
    }
