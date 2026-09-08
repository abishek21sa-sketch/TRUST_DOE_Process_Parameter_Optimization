from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.optimize import differential_evolution
from .domain import CampaignState, ProcessSpace
from .doe import quadratic_features
from .surrogate import GPSurrogate
from .calibration import CalibrationResult, cross_validated_conformal
from .controller import CandidateDecision


@dataclass(frozen=True)
class AcquisitionConfig:
    beta: float = 1.64
    lambda_improvement: float = 1.0
    lambda_information: float = 0.18
    distance_penalty: float = 0.04
    conformal_coverage: float = 0.90
    optimizer_maxiter: int = 55
    population_size: int = 11


@dataclass(frozen=True)
class AcquisitionDiagnostics:
    objective_calibration: CalibrationResult
    safety_calibration: CalibrationResult
    evaluations: int
    optimizer_success: bool
    optimizer_message: str


def _information_gain_fast(observed_z: np.ndarray):
    X = quadratic_features(observed_z)
    M = X.T @ X + 1e-6 * np.eye(X.shape[1])
    inv = np.linalg.inv(M)

    def gain(z: np.ndarray) -> float:
        phi = quadratic_features(np.asarray(z))[0]
        val = float(phi @ inv @ phi)
        return float(np.log1p(max(0.0, val)))

    return gain


def _conformal_halfwidth(std: float, calibration: CalibrationResult, beta: float) -> float:
    return max(beta * float(std), calibration.absolute_error_quantile)


def optimize_next_experiment(
    state: CampaignState,
    space: ProcessSpace,
    config: AcquisitionConfig = AcquisitionConfig(),
    seed: int = 2026,
) -> tuple[CandidateDecision, AcquisitionDiagnostics]:
    """Continuously optimize TRUST-DOE-S acquisition in normalized process coordinates.

    The candidate must satisfy both the adaptive trust-region and a conservative calibrated
    safety lower bound. The result is always shadow-only.
    """
    incumbent = state.incumbent()
    center_z = space.normalize(incumbent.recipe)
    observed_z = np.array([space.normalize(o.recipe) for o in state.observations])
    obj_gp = GPSurrogate(space, seed=seed + 1).fit(state.observations, "objective")
    safe_gp = GPSurrogate(space, seed=seed + 2).fit(state.observations, "safety_margin")
    obj_cal = cross_validated_conformal(space, state.observations, "objective", config.conformal_coverage, seed=seed + 3)
    safe_cal = cross_validated_conformal(space, state.observations, "safety_margin", config.conformal_coverage, seed=seed + 4)
    info_gain = _information_gain_fast(observed_z)
    eval_count = 0

    def evaluate_z(z: np.ndarray) -> tuple[float, CandidateDecision | None]:
        nonlocal eval_count
        eval_count += 1
        z = np.asarray(z, dtype=float)
        dist = float(np.linalg.norm(z - center_z))
        if dist > state.trust_radius:
            return 1e4 + 1e3 * (dist - state.trust_radius), None
        recipe = space.denormalize(z)
        obj = obj_gp.predict(np.array([recipe]))
        safe = safe_gp.predict(np.array([recipe]))
        obj_hw = _conformal_halfwidth(float(obj.std[0]), obj_cal, config.beta)
        safe_hw = _conformal_halfwidth(float(safe.std[0]), safe_cal, config.beta)
        safe_lower = float(safe.mean[0] - safe_hw)
        if safe_lower < 0.0:
            return 5e3 + 2e3 * abs(safe_lower), None
        obj_upper = float(obj.mean[0] + obj_hw)
        improvement = max(0.0, incumbent.objective - obj_upper)
        gain = info_gain(z)
        score = (
            config.lambda_improvement * improvement
            + config.lambda_information * gain
            - config.distance_penalty * dist
        )
        dec = CandidateDecision(
            tuple(map(float, recipe)),
            float(obj.mean[0]),
            float(obj_hw),  # calibrated half-width carried in existing std field
            float(safe.mean[0]),
            float(safe_hw),
            improvement,
            gain,
            dist,
            float(score),
            True,
            False,
        )
        return -score, dec

    def objective(z: np.ndarray) -> float:
        return evaluate_z(z)[0]

    result = differential_evolution(
        objective,
        bounds=[(-1.0, 1.0)] * space.dimension,
        seed=seed,
        maxiter=config.optimizer_maxiter,
        popsize=config.population_size,
        polish=True,
        updating="immediate",
        workers=1,
        tol=1e-6,
    )
    _, decision = evaluate_z(result.x)
    if decision is None:
        # deterministic rescue: progressively expand candidate samples inside trust radius.
        rng = np.random.default_rng(seed + 991)
        best: CandidateDecision | None = None
        for _ in range(6000):
            z = np.clip(center_z + rng.normal(0.0, max(0.04, state.trust_radius / 3.0), space.dimension), -1, 1)
            _, dec = evaluate_z(z)
            if dec is not None and (best is None or dec.score > best.score):
                best = dec
        if best is None:
            raise RuntimeError("Continuous acquisition found no calibrated-safe candidate")
        decision = best
    diagnostics = AcquisitionDiagnostics(obj_cal, safe_cal, eval_count, bool(result.success), str(result.message))
    return decision, diagnostics
