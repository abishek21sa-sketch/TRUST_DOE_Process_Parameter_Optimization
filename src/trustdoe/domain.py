from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable
import numpy as np

@dataclass(frozen=True)
class Factor:
    name: str
    low: float
    high: float
    unit: str

    def normalize(self, x: float) -> float:
        if self.high <= self.low:
            raise ValueError(f"Invalid bounds for {self.name}")
        return 2.0 * (x - self.low) / (self.high - self.low) - 1.0

    def denormalize(self, z: float) -> float:
        return self.low + (z + 1.0) * 0.5 * (self.high - self.low)

@dataclass(frozen=True)
class ProcessSpace:
    factors: tuple[Factor, ...]

    @property
    def dimension(self) -> int:
        return len(self.factors)

    @property
    def lows(self) -> np.ndarray:
        return np.array([f.low for f in self.factors], dtype=float)

    @property
    def highs(self) -> np.ndarray:
        return np.array([f.high for f in self.factors], dtype=float)

    def normalize(self, x: Iterable[float]) -> np.ndarray:
        x = np.asarray(list(x), dtype=float)
        if x.shape != (self.dimension,):
            raise ValueError("Recipe dimension mismatch")
        return np.array([f.normalize(v) for f, v in zip(self.factors, x)], dtype=float)

    def denormalize(self, z: Iterable[float]) -> np.ndarray:
        z = np.asarray(list(z), dtype=float)
        return np.array([f.denormalize(v) for f, v in zip(self.factors, z)], dtype=float)

    def contains(self, x: Iterable[float], atol: float = 1e-12) -> bool:
        x = np.asarray(list(x), dtype=float)
        return bool(np.all(x >= self.lows - atol) and np.all(x <= self.highs + atol))

@dataclass(frozen=True)
class Observation:
    recipe: tuple[float, ...]
    objective: float
    safety_margin: float
    source: str = "SYNTHETIC_BENCHMARK"

    @property
    def safe(self) -> bool:
        return self.safety_margin >= 0.0

@dataclass
class CampaignState:
    observations: list[Observation] = field(default_factory=list)
    trust_radius: float = 0.55
    iteration: int = 0

    def append(self, observation: Observation) -> None:
        self.observations.append(observation)
        self.iteration += 1

    def safe_observations(self) -> list[Observation]:
        return [o for o in self.observations if o.safe]

    def incumbent(self) -> Observation:
        safe = self.safe_observations()
        if not safe:
            raise RuntimeError("No safe incumbent exists")
        return min(safe, key=lambda o: o.objective)
