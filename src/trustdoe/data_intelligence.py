"""Auditable CSV/Parquet ingestion and dataset evidence."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib, json, re
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class DatasetEvidence:
    dataset_id: str; sha256: str; rows: int; factors: list[str]; responses: list[str]
    missing: dict[str, int]; warnings: list[str]; readiness: str
    distributions: dict[str, dict[str, float]]; version: int = 1
    def to_dict(self): return asdict(self)
    def to_json(self, path):
        target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8"); return target

_RESP = re.compile(r"(response|result|objective|quality|throughput|cost|energy|defect|yield|output)", re.I)
_ID = re.compile(r"(^id$|time|date|batch|run|sample|operator)", re.I)

def inspect_dataset(path, *, expected_units=None, factor_columns=None, response_columns=None):
    path = Path(path); raw = path.read_bytes()
    if path.suffix.lower() == '.csv': frame = pd.read_csv(path)
    elif path.suffix.lower() == '.parquet': frame = pd.read_parquet(path)
    else: raise ValueError('Unsupported dataset format; use CSV or Parquet')
    if frame.empty: raise ValueError('Dataset has no rows')
    factors = list(factor_columns or [c for c in frame.select_dtypes(include=np.number).columns if not _RESP.search(c) and not _ID.search(c)])
    responses = list(response_columns or [c for c in frame.columns if _RESP.search(c)])
    missing = {str(c): int(n) for c, n in frame.isna().sum().items() if n}; warnings = []
    if not factors: warnings.append('No factor columns detected; provide factor_columns explicitly')
    if not responses: warnings.append('No response columns detected; provide response_columns explicitly')
    if missing: warnings.append('Missing values present; no imputation was performed')
    if expected_units:
        absent = sorted(set(expected_units) - set(frame.columns))
        if absent: warnings.append(f'Unit metadata missing for columns: {absent}')
    distributions = {}
    for col in frame.select_dtypes(include=np.number).columns:
        s = frame[col].dropna()
        if len(s):
            q1, q3 = s.quantile([.25, .75]); iqr = q3-q1
            out = int(((s < q1-1.5*iqr) | (s > q3+1.5*iqr)).sum()) if iqr else 0
            distributions[col] = {'min': float(s.min()), 'max': float(s.max()), 'mean': float(s.mean()), 'std': float(s.std(ddof=0)), 'outliers_iqr': out}
    digest = hashlib.sha256(raw).hexdigest()
    return DatasetEvidence('DS-'+digest[:12], digest, len(frame), factors, responses, missing, warnings, 'READY_WITH_WARNINGS' if warnings else 'READY', distributions)
