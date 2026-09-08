from __future__ import annotations
from pathlib import Path
import pandas as pd, hashlib
from .process import DEFAULT_SPACE

REQUIRED=[f.name for f in DEFAULT_SPACE.factors]+['objective','safety_margin']

def inspect_csv(path:str|Path)->dict:
    path=Path(path); raw=path.read_bytes(); df=pd.read_csv(path)
    missing=[c for c in REQUIRED if c not in df.columns]
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(df),'columns':list(df.columns),
            'required_fields':REQUIRED,'missing_fields':missing,'ready':not missing,
            'evidence_class':'USER_SUPPLIED_HISTORICAL_DATA' if not missing else 'NOT_READY'}

def public_source_manifest()->list[dict]:
    return [
      {'source':'NIST AM Bench','mode':'PUBLIC_DATA_ADAPTER','status':'ADAPTER_CONTRACT_DEFINED','validation':'EXTERNAL_DATASET_EXECUTION_PENDING',
       'boundary':'User must acquire/download the governed dataset; this repository does not fabricate missing AM Bench fields.'}
    ]
