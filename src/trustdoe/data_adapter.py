from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib
import pandas as pd
from .domain import Observation, ProcessSpace

@dataclass(frozen=True)
class IngestReport:
    rows: int
    sha256: str
    evidence_class: str

REQUIRED = ["objective", "safety_margin"]

def ingest_experiment_csv(path: str | Path, space: ProcessSpace) -> tuple[list[Observation], IngestReport]:
    path = Path(path)
    raw = path.read_bytes()
    df = pd.read_csv(path)
    factor_names = [f.name for f in space.factors]
    missing = [c for c in factor_names + REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    obs = []
    for _, row in df.iterrows():
        recipe = tuple(float(row[c]) for c in factor_names)
        if not space.contains(recipe):
            raise ValueError("Input row outside governed process bounds")
        obs.append(Observation(recipe, float(row.objective), float(row.safety_margin), source="USER_SUPPLIED_HISTORICAL"))
    return obs, IngestReport(len(obs), hashlib.sha256(raw).hexdigest(), "USER_SUPPLIED_HISTORICAL")
