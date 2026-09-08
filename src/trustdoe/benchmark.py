from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .process import SyntheticAMOracle
from .campaign import run_closed_loop, initialize_campaign
from .doe import latin_hypercube, information_logdet

@dataclass(frozen=True)
class StrategyMetrics:
    strategy: str
    best_safe_objective: float
    information_logdet: float
    unsafe_trials: int
    trials: int


def _metrics(strategy: str, oracle: SyntheticAMOracle, observations) -> StrategyMetrics:
    safe = [o.objective for o in observations if o.safe]
    z = np.array([oracle.space.normalize(o.recipe) for o in observations])
    return StrategyMetrics(strategy, min(safe) if safe else float("inf"), information_logdet(z), sum(not o.safe for o in observations), len(observations))


def compare_strategies(budget: int = 8, seed: int = 222) -> list[StrategyMetrics]:
    # common initial design, independent deterministic oracle seeds after initialization
    oracle_t = SyntheticAMOracle(seed=seed)
    trust = run_closed_loop(oracle_t, budget=budget, seed=seed)
    trust_m = _metrics("TRUST-DOE", oracle_t, trust.state.observations)

    oracle_r = SyntheticAMOracle(seed=seed)
    random_state = initialize_campaign(oracle_r, n_initial=14, seed=seed)
    for x in latin_hypercube(oracle_r.space, budget, seed=seed+500):
        random_state.append(oracle_r.evaluate(x))
    random_m = _metrics("RANDOM-LHS", oracle_r, random_state.observations)
    return [trust_m, random_m]
