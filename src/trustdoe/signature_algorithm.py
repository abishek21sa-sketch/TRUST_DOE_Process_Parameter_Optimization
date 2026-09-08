"""TRUST-DOE safe recipe and information-gain reference contract."""

from math import sqrt


def select_recipe(candidates, center, trust_radius, min_safety):
    if trust_radius < 0:
        raise ValueError("trust radius must be nonnegative")
    feasible = []
    for candidate in candidates:
        distance = sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(candidate["recipe"], center)))
        if distance <= trust_radius and candidate["safety"] >= min_safety:
            score = float(candidate["objective"]) - float(candidate.get("information", 0.0))
            feasible.append({**candidate, "distance": distance, "score": score})
    return min(feasible, key=lambda x: (x["score"], x["distance"])) if feasible else None


def ablation(candidates, center, trust_radius, min_safety):
    """Remove the trust-region constraint for a declared extrapolation ablation."""
    return select_recipe(candidates, center, float("inf"), min_safety)


def sensitivity(candidates, center, trust_radius, min_safety, safety_delta):
    return select_recipe(candidates, center, trust_radius, min_safety + safety_delta)
