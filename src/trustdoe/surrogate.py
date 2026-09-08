from __future__ import annotations
from dataclasses import dataclass
import warnings
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.exceptions import ConvergenceWarning
from .domain import ProcessSpace, Observation

@dataclass
class Prediction:
    mean: np.ndarray
    std: np.ndarray

class GPSurrogate:
    def __init__(self, space: ProcessSpace, seed: int = 5):
        self.space = space
        d = space.dimension
        kernel = ConstantKernel(1.0, (1e-3, 1e3))*Matern(length_scale=np.ones(d), length_scale_bounds=(0.08, 5.0), nu=2.5) + WhiteKernel(1e-4, (1e-7, 5e-2))
        self.model = GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=1, random_state=seed)
        self._fit = False

    def fit(self, observations: list[Observation], target: str) -> "GPSurrogate":
        if len(observations) < max(5, self.space.dimension + 1):
            raise ValueError("Insufficient observations for GP surrogate")
        X = np.array([self.space.normalize(o.recipe) for o in observations])
        y = np.array([getattr(o, target) for o in observations], dtype=float)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            self.model.fit(X, y)
        self._fit = True
        return self

    def predict(self, recipes: np.ndarray) -> Prediction:
        if not self._fit:
            raise RuntimeError("Surrogate not fitted")
        X = np.array([self.space.normalize(r) for r in np.atleast_2d(recipes)])
        mean, std = self.model.predict(X, return_std=True)
        return Prediction(np.asarray(mean), np.maximum(np.asarray(std), 1e-9))
