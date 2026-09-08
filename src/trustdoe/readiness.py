from __future__ import annotations
from dataclasses import dataclass, asdict
import pandas as pd

CANONICAL_COLUMNS=["laser_power","scan_speed","hatch_spacing","layer_thickness","objective","safety_margin"]
@dataclass
class ReadinessReport:
    ready: bool
    rows: int
    missing_columns: list[str]
    null_counts: dict[str,int]
    duplicated_rows: int
    label: str

def assess_frame(df: pd.DataFrame) -> ReadinessReport:
    missing=[c for c in CANONICAL_COLUMNS if c not in df.columns]
    nulls={c:int(df[c].isna().sum()) for c in CANONICAL_COLUMNS if c in df.columns}
    ready=(not missing) and all(v==0 for v in nulls.values()) and len(df)>=12
    return ReadinessReport(ready,len(df),missing,nulls,int(df.duplicated().sum()),"READY" if ready else "NOT_READY")
def readiness_payload(df): return asdict(assess_frame(df))
