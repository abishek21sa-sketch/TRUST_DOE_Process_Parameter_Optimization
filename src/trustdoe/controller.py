from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .domain import CampaignState, ProcessSpace
from .doe import quadratic_features
from .surrogate import GPSurrogate

@dataclass(frozen=True)
class CandidateDecision:
    recipe: tuple[float, ...]
    predicted_objective: float
    objective_std: float
    predicted_safety: float
    safety_std: float
    conservative_improvement: float
    information_gain: float
    normalized_distance: float
    score: float
    safe_by_model: bool
    production_write_allowed: bool = False


def _logdet_gain(observed_z: np.ndarray, candidate_z: np.ndarray, ridge: float = 1e-6) -> float:
    X = quadratic_features(observed_z)
    phi = quadratic_features(candidate_z)[0]
    M = X.T @ X + ridge*np.eye(X.shape[1])
    sign0, ld0 = np.linalg.slogdet(M)
    M2 = M + np.outer(phi, phi)
    sign1, ld1 = np.linalg.slogdet(M2)
    if sign0 <= 0 or sign1 <= 0:
        return 0.0
    return float(ld1 - ld0)


def select_next_experiment(
    state: CampaignState,
    space: ProcessSpace,
    candidates: np.ndarray,
    beta: float = 1.64,
    lambda_improvement: float = 1.0,
    lambda_information: float = 0.18,
    distance_penalty: float = 0.04,
) -> CandidateDecision:
    incumbent = state.incumbent()
    center_z = space.normalize(incumbent.recipe)
    observed_z = np.array([space.normalize(o.recipe) for o in state.observations])

    obj_gp = GPSurrogate(space, seed=5).fit(state.observations, "objective")
    safe_gp = GPSurrogate(space, seed=7).fit(state.observations, "safety_margin")
    obj_pred = obj_gp.predict(candidates)
    safe_pred = safe_gp.predict(candidates)

    best = None
    for i, recipe in enumerate(candidates):
        z = space.normalize(recipe)
        dist = float(np.linalg.norm(z-center_z))
        if dist > state.trust_radius + 1e-12:
            continue
        safe_lower = float(safe_pred.mean[i] - beta*safe_pred.std[i])
        safe = safe_lower >= 0.0
        if not safe:
            continue
        obj_upper = float(obj_pred.mean[i] + beta*obj_pred.std[i])
        imp = max(0.0, incumbent.objective - obj_upper)
        gain = _logdet_gain(observed_z, z)
        score = lambda_improvement*imp + lambda_information*gain - distance_penalty*dist
        dec = CandidateDecision(tuple(map(float, recipe)), float(obj_pred.mean[i]), float(obj_pred.std[i]),
                                float(safe_pred.mean[i]), float(safe_pred.std[i]), imp, gain, dist, score, True, False)
        if best is None or dec.score > best.score:
            best = dec
    if best is None:
        raise RuntimeError("No model-safe candidate inside current trust region")
    return best


def adapt_trust_region(state: CampaignState, previous_best: float, decision: CandidateDecision, observed_objective: float, observed_safe: bool,
                       min_radius: float = 0.12, max_radius: float = 1.25) -> float:
    if not observed_safe:
        state.trust_radius = max(min_radius, state.trust_radius*0.55)
        return state.trust_radius
    predicted = max(decision.conservative_improvement, 1e-9)
    realized = previous_best - observed_objective
    ratio = realized / predicted if predicted > 1e-8 else 0.0
    if ratio < 0.25:
        state.trust_radius = max(min_radius, state.trust_radius*0.72)
    elif ratio > 0.75:
        state.trust_radius = min(max_radius, state.trust_radius*1.18)
    return state.trust_radius
