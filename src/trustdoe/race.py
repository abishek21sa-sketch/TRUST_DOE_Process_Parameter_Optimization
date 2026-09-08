from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.optimize import differential_evolution
from .process import SyntheticAMOracle
from .campaign import initialize_campaign
from .domain import CampaignState
from .doe import latin_hypercube, factorial_points, information_logdet
from .surrogate import GPSurrogate
from .acquisition import AcquisitionConfig, optimize_next_experiment
from .controller import adapt_trust_region


@dataclass(frozen=True)
class RacePoint:
    trial: int
    best_safe_objective: float
    information_logdet: float
    unsafe_trials: int


@dataclass(frozen=True)
class RaceResult:
    strategy: str
    points: tuple[RacePoint, ...]
    final_best_safe_objective: float
    final_information_logdet: float
    unsafe_trials: int
    production_write_allowed: bool = False


def _point(oracle: SyntheticAMOracle, state: CampaignState, trial: int) -> RacePoint:
    safe = [o.objective for o in state.observations if o.safe]
    z = np.array([oracle.space.normalize(o.recipe) for o in state.observations])
    return RacePoint(trial, min(safe) if safe else float("inf"), information_logdet(z), sum(not o.safe for o in state.observations))


def _unconstrained_bo_recipe(oracle: SyntheticAMOracle, state: CampaignState, seed: int) -> np.ndarray:
    gp = GPSurrogate(oracle.space, seed=seed).fit(state.observations, "objective")
    def lcb(z):
        recipe = oracle.space.denormalize(z)
        p = gp.predict(np.array([recipe]))
        return float(p.mean[0] - 1.35 * p.std[0])
    res = differential_evolution(lcb, [(-1, 1)] * oracle.space.dimension, seed=seed, maxiter=32, popsize=8, polish=True)
    return oracle.space.denormalize(res.x)


def run_strategy(strategy: str, budget: int = 8, seed: int = 2026) -> RaceResult:
    oracle = SyntheticAMOracle(seed=seed)
    state = initialize_campaign(oracle, n_initial=14, seed=seed)
    points = [_point(oracle, state, 0)]
    static_design = factorial_points(oracle.space, center=True)
    random_design = latin_hypercube(oracle.space, budget, seed=seed + 500)

    for k in range(budget):
        previous_best = state.incumbent().objective
        if strategy == "TRUST-DOE-S":
            cfg = AcquisitionConfig(optimizer_maxiter=28, population_size=8)
            try:
                decision, _ = optimize_next_experiment(state, oracle.space, cfg, seed=seed + 100 + k)
                recipe = np.asarray(decision.recipe)
            except RuntimeError:
                # Calibrated intervals can be deliberately conservative early in a campaign.
                # A shadow-only local probe inside the verified region is the fallback.
                rng = np.random.default_rng(seed + 9900 + k)
                z0 = oracle.space.normalize(state.incumbent().recipe)
                z = np.clip(z0 + rng.normal(0.0, min(0.12, state.trust_radius / 4), oracle.space.dimension), -1, 1)
                recipe = oracle.space.denormalize(z)
                decision = None
        elif strategy == "RANDOM-LHS":
            recipe = random_design[k]
            decision = None
        elif strategy == "STATIC-DOE":
            recipe = static_design[k % len(static_design)]
            decision = None
        elif strategy == "UNCONSTRAINED-BO":
            recipe = _unconstrained_bo_recipe(oracle, state, seed + 300 + k)
            decision = None
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        obs = oracle.evaluate(recipe)
        state.append(obs)
        if strategy == "TRUST-DOE-S" and decision is not None:
            adapt_trust_region(state, previous_best, decision, obs.objective, obs.safe)
        points.append(_point(oracle, state, k + 1))

    final = points[-1]
    return RaceResult(strategy, tuple(points), final.best_safe_objective, final.information_logdet, final.unsafe_trials, False)


def experiment_race(budget: int = 8, seed: int = 2026) -> list[RaceResult]:
    return [run_strategy(s, budget, seed) for s in ("TRUST-DOE-S", "RANDOM-LHS", "STATIC-DOE", "UNCONSTRAINED-BO")]


def race_payload(results: list[RaceResult]) -> list[dict]:
    return [asdict(r) for r in results]
