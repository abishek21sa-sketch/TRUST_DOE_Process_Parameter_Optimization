from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from .domain import ProcessSpace
from .process import SyntheticAMOracle

@dataclass(frozen=True)
class RobustnessResult:
    expected_objective: float
    objective_p95: float
    feasibility_probability: float
    samples: int


def stress_recipe(oracle: SyntheticAMOracle, recipe: np.ndarray, relative_sigma: float = 0.015, n: int = 3000, seed: int = 999) -> RobustnessResult:
    rng = np.random.default_rng(seed)
    span = oracle.space.highs-oracle.space.lows
    perturb = rng.normal(0.0, relative_sigma*span, size=(n, oracle.space.dimension))
    samples = np.clip(recipe + perturb, oracle.space.lows, oracle.space.highs)
    vals = np.array([oracle.noiseless(x) for x in samples])
    return RobustnessResult(float(vals[:,0].mean()), float(np.quantile(vals[:,0], 0.95)), float((vals[:,1] >= 0).mean()), n)
