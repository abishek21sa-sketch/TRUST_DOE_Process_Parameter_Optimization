from __future__ import annotations
from dataclasses import dataclass
import warnings
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.model_selection import KFold
from sklearn.exceptions import ConvergenceWarning
from .domain import ProcessSpace, Observation


@dataclass(frozen=True)
class CalibrationResult:
    target: str
    coverage: float
    absolute_error_quantile: float
    folds: int
    samples: int


def _new_gp(d: int, seed: int) -> GaussianProcessRegressor:
    kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
        length_scale=np.ones(d), length_scale_bounds=(0.08, 5.0), nu=2.5
    ) + WhiteKernel(1e-4, (1e-7, 5e-2))
    return GaussianProcessRegressor(kernel=kernel, normalize_y=True, n_restarts_optimizer=0, random_state=seed)


def cross_validated_conformal(
    space: ProcessSpace,
    observations: list[Observation],
    target: str,
    coverage: float = 0.90,
    folds: int = 4,
    seed: int = 77,
) -> CalibrationResult:
    """Estimate a distribution-free absolute residual radius using K-fold out-of-fold predictions.

    This is a finite-sample diagnostic/calibration layer for the synthetic benchmark.  It does not
    assert real factory coverage without external validation.
    """
    if not 0.5 < coverage < 1.0:
        raise ValueError("coverage must be between 0.5 and 1")
    n = len(observations)
    if n < max(8, folds * 2):
        raise ValueError("Insufficient observations for conformal calibration")
    X = np.array([space.normalize(o.recipe) for o in observations])
    y = np.array([getattr(o, target) for o in observations], dtype=float)
    kf = KFold(n_splits=min(folds, n // 2), shuffle=True, random_state=seed)
    residuals: list[float] = []
    for split, (train, test) in enumerate(kf.split(X)):
        gp = _new_gp(space.dimension, seed + split)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            gp.fit(X[train], y[train])
        pred = gp.predict(X[test])
        residuals.extend(np.abs(y[test] - pred).tolist())
    residuals_arr = np.asarray(residuals, dtype=float)
    # Conservative finite-sample order statistic.
    rank = int(np.ceil((len(residuals_arr) + 1) * coverage)) - 1
    rank = max(0, min(rank, len(residuals_arr) - 1))
    q = float(np.sort(residuals_arr)[rank])
    return CalibrationResult(target, coverage, q, kf.n_splits, len(residuals_arr))
