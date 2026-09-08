from __future__ import annotations
import json, tempfile, time
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT/'src'):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
from trustdoe.workflow import WorkflowService
from trustdoe.governance import verify_release_certificate

start=time.perf_counter()
with tempfile.TemporaryDirectory() as td:
    svc=WorkflowService(Path(td)/'trustdoe.db')
    created=svc.create_campaign('enterprise-operability',runs=12,seed=2026)
    cid=created['campaign']['id']
    cert=svc.release_assurance(cid,seed=2026,n_candidates=16,stress_samples=80)
    tampered=deepcopy(cert); tampered['decision_state']='PRODUCTION_RELEASED'
    tamper=verify_release_certificate(tampered)
    out_of_bounds_rejected=False
    try:
        svc.record_observation(cid,[9999,9999,9999,9999],objective=.1,safety_margin=.5)
    except ValueError:
        out_of_bounds_rejected=True
elapsed=time.perf_counter()-start
checks={
    'certificate_integrity_valid':cert['verification']['valid'] is True,
    'production_write_blocked':cert['production_write_allowed'] is False,
    'tampering_detected':tamper['valid'] is False,
    'out_of_bounds_recipe_rejected':out_of_bounds_rejected,
    'reference_runtime_under_30s':elapsed < 30,
}
payload={'phase':'ENTERPRISE_OPERABILITY_V1','status':'PASS' if all(checks.values()) else 'HOLD','checks':checks,'runtime_seconds':elapsed,'decision_state':cert['decision_state'],'certificate_sha256':cert['certificate_sha256'],'claim_boundary':'Synthetic process-development operability evidence only; production recipe write remains blocked.'}
(ROOT/'artifacts'/'enterprise_operability.json').write_text(json.dumps(payload,indent=2,sort_keys=True,default=str))
print(json.dumps({'status':payload['status'],'checks':checks,'runtime_seconds':round(elapsed,3),'decision_state':cert['decision_state']},indent=2))
if payload['status']!='PASS': raise SystemExit('TRUST_DOE_ENTERPRISE_OPERABILITY=HOLD')
print('TRUST_DOE_ENTERPRISE_OPERABILITY=PASS')
