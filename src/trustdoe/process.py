from __future__ import annotations
import numpy as np
from .domain import Factor, ProcessSpace, Observation

DEFAULT_SPACE = ProcessSpace((
    Factor("laser_power", 160.0, 320.0, "W"),
    Factor("scan_speed", 600.0, 1400.0, "mm/s"),
    Factor("hatch_spacing", 0.07, 0.14, "mm"),
    Factor("layer_thickness", 0.02, 0.06, "mm"),
))

class SyntheticAMOracle:
    """Deterministic seeded digital experiment oracle.

    It is a synthetic benchmark, not a representation of a specific machine.
    Lower objective is better. Safety margin >= 0 denotes a feasible melt/quality window.
    """
    def __init__(self, space: ProcessSpace = DEFAULT_SPACE, noise_std: float = 0.015, seed: int = 17):
        self.space = space
        self.noise_std = float(noise_std)
        self.rng = np.random.default_rng(seed)

    def noiseless(self, recipe: np.ndarray) -> tuple[float, float]:
        z = self.space.normalize(recipe)
        p, v, h, t = z
        objective = (
            0.55*(p-0.18)**2 + 0.75*(v+0.12)**2 + 0.50*(h-0.08)**2 + 0.60*(t+0.10)**2
            + 0.22*p*v - 0.16*v*h + 0.12*p*t + 0.08*np.sin(2.2*p - 1.4*v)
        )
        # safety as robust operating-window proxy; positive inside curved feasible band
        safety = 1.05 - 0.42*(p+0.18)**2 - 0.30*(v-0.10)**2 - 0.35*(h+0.10)**2 - 0.25*(t-0.08)**2 - 0.12*p*v
        return float(objective), float(safety)

    def evaluate(self, recipe: np.ndarray) -> Observation:
        if not self.space.contains(recipe):
            raise ValueError("Recipe outside governed process bounds")
        obj, safety = self.noiseless(recipe)
        obj += float(self.rng.normal(0, self.noise_std))
        safety += float(self.rng.normal(0, self.noise_std * 0.5))
        return Observation(tuple(map(float, recipe)), obj, safety, source="SYNTHETIC_BENCHMARK")
