from __future__ import annotations
from pathlib import Path
import json
from .process import SyntheticAMOracle
from .campaign import run_closed_loop
from .design_studio import design_catalog
from .model_lab import model_lab_payload
from .process_science import process_science_payload
from .or_engine import or_payload
from .scenario_lab import scenario_matrix
from .qualification import qualification_gate
from .data_gateway import public_source_manifest
from .persistence import CampaignRepository


def build_phased_evidence(root: str|Path='.', seed:int=2026)->dict:
    root=Path(root); oracle=SyntheticAMOracle(seed=seed)
    campaign=run_closed_loop(oracle,budget=18,seed=seed)
    obs=campaign.state.observations
    incumbent=campaign.state.incumbent()
    scenarios=scenario_matrix(oracle,incumbent.recipe)
    worst=min(scenarios,key=lambda x:x['feasibility_probability'])
    q=qualification_gate(feasibility_probability=worst['feasibility_probability'], safety_p05=worst['safety_p05'],
                         evidence_class='SYNTHETIC_VALIDATION', data_ready=True, model_validated=True)
    payload={
      'version':'0.96.0','phase':'D','evidence_class':'SYNTHETIC_VALIDATION',
      'product':'TRUST-DOE Process Development Platform','signature_algorithm':'TRUST-DOE-S',
      'production_write_allowed':False,
      'workspaces':['Experiment Design Studio','Model Laboratory','Autonomous Experiment Studio','Operating Window Explorer','Recipe Forge','Qualification Gate','Scenario Laboratory','Campaign Ledger','Data Gateway'],
      'design_studio':design_catalog(oracle.space,seed),
      'model_laboratory':model_lab_payload(oracle.space,obs),
      'process_science':process_science_payload(oracle.space,obs),
      'operations_research':or_payload(oracle),
      'scenario_laboratory':scenarios,
      'qualification_gate':q,
      'public_data_sources':public_source_manifest(),
      'campaign':{
        'iterations':campaign.state.iteration,'trust_radius':campaign.state.trust_radius,
        'incumbent':{'recipe':list(incumbent.recipe),'objective':incumbent.objective,'safety_margin':incumbent.safety_margin,'source':incumbent.source},
        'observations':[{'iteration':i+1,'recipe':list(o.recipe),'objective':o.objective,'safety_margin':o.safety_margin,'safe':o.safe,'source':o.source} for i,o in enumerate(obs)]
      },
      'governance':{'decision_mode':'SHADOW_EXPERIMENT_ONLY','external_validation':'PENDING','machine_write':'BLOCKED'}
    }
    (root/'artifacts').mkdir(parents=True,exist_ok=True); (root/'workbench').mkdir(parents=True,exist_ok=True); (root/'runtime').mkdir(parents=True,exist_ok=True)
    (root/'artifacts'/'phaseD_report.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    (root/'workbench'/'data_phaseD.json').write_text(json.dumps(payload),encoding='utf-8')
    repo=CampaignRepository(root/'runtime'/'trustdoe.db')
    cid='DEMO-2026-001'; repo.upsert_campaign(cid,'Synthetic qualification campaign',metadata={'seed':seed,'version':'0.96.0'})
    # idempotent rebuild through repository lifecycle (Windows-safe handle closure)
    repo.clear_campaign_children(cid)
    for i,o in enumerate(obs,1): repo.append_observation(cid,i,o)
    repo.record_decision(cid,'QUALIFICATION_GATE',q)
    return payload
