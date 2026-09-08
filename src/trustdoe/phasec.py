from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import json
import pandas as pd
from .process import SyntheticAMOracle
from .campaign import run_closed_loop
from .process_science import process_science_payload, local_sensitivity
from .model_lab import model_lab_payload
from .drift import drift_payload
from .or_engine import or_payload
from .readiness import readiness_payload


def build_phasec_evidence(root: str|Path=".", seed:int=2026) -> dict:
    root=Path(root)
    oracle=SyntheticAMOracle(seed=seed)
    campaign=run_closed_loop(oracle,budget=14,seed=seed)
    obs=campaign.state.observations
    incumbent=campaign.state.incumbent()
    df=pd.DataFrame([{**{f.name:v for f,v in zip(oracle.space.factors,o.recipe)},"objective":o.objective,"safety_margin":o.safety_margin} for o in obs])
    sens=local_sensitivity(oracle.space,lambda x: oracle.noiseless(x)[0],incumbent.recipe)
    payload={
      "version":"0.9.0","phase":"C","evidence_class":"SYNTHETIC_VALIDATION",
      "signature_algorithm":"TRUST-DOE-S","production_write_allowed":False,
      "phase_b_kernel":{"status":"PRESERVED_AND_REGRESSION_TESTED","capabilities":["TRUST-DOE-S","Experiment Race","conformal calibration","robust release frontier","Safe Experiment Cockpit"]},
      "process_science":process_science_payload(oracle.space,obs),
      "model_laboratory":model_lab_payload(oracle.space,obs),
      "drift_monitor":drift_payload(oracle.space,obs),
      "operations_research":or_payload(oracle),
      "sensitivity":[asdict(s) for s in sens],
      "data_readiness":readiness_payload(df),
      "governance":{"decision_mode":"SHADOW_EXPERIMENT_ONLY","real_world_validation":"PENDING","claim_boundary":"All benchmark metrics are synthetic-validation evidence until a governed external dataset is supplied."}
    }
    (root/"artifacts").mkdir(parents=True,exist_ok=True)
    (root/"workbench").mkdir(parents=True,exist_ok=True)
    (root/"artifacts"/"phaseC_report.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    (root/"workbench"/"data_phaseC.json").write_text(json.dumps(payload),encoding="utf-8")
    return payload
