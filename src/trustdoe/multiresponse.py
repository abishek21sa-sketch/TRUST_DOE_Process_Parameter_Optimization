"""Multi-response preference scoring and Pareto frontier utilities."""
from __future__ import annotations
import numpy as np


def _directions(n: int, directions):
    d = np.ones(n, dtype=float) if directions is None else np.asarray(directions, dtype=float)
    if d.shape != (n,) or not np.all(np.isin(d, [-1.0, 1.0])):
        raise ValueError("directions must contain exactly one +/-1 value per response")
    return d


def weighted_score(values, weights, directions=None):
    x = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if x.ndim != 2 or w.shape != (x.shape[1],) or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("invalid values or weights")
    d = _directions(x.shape[1], directions)
    lo, hi = x.min(0), x.max(0)
    span = np.where(hi > lo, hi - lo, 1.0)
    u = (x - lo) / span
    u = np.where(d > 0, u, 1 - u)
    return u @ (w / w.sum())


def pareto_frontier(values, directions=None, feasible=None):
    """Return indices of nondominated feasible observations.

    Direction +1 means maximize, -1 means minimize. Infeasible observations are
    excluded from both the returned frontier and the dominance set, which is the
    intended behavior for qualified operating-window discovery.
    """
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or len(x) == 0:
        raise ValueError("values must be a non-empty 2D array")
    d = _directions(x.shape[1], directions)
    if feasible is None:
        feasible_mask = np.ones(len(x), dtype=bool)
    else:
        feasible_mask = np.asarray(feasible, dtype=bool)
        if feasible_mask.shape != (len(x),):
            raise ValueError("feasible mask must contain one boolean per observation")
    utility = x * d
    feasible_utility = utility[feasible_mask]
    result: list[int] = []
    for i in range(len(x)):
        if not feasible_mask[i]:
            continue
        dominates = ((feasible_utility >= utility[i]).all(1) & (feasible_utility > utility[i]).any(1)).any()
        if not dominates:
            result.append(i)
    return np.asarray(result, dtype=int)
