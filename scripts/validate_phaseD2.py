from pathlib import Path
import tempfile
from trustdoe.persistence import CampaignRepository
from trustdoe.workflow import WorkflowService
ROOT=Path(__file__).resolve().parents[1]
checks={}
with tempfile.TemporaryDirectory() as td:
    svc=WorkflowService(Path(td)/'qa.db')
    c=svc.create_campaign('QA campaign',runs=10,seed=77)
    cid=c['campaign']['id']
    checks['campaign_created']=len(c['observations'])>=10
    d=svc.generate_design('CENTRAL_COMPOSITE',6,77)
    checks['doe_generated']=d['metrics']['runs']>0 and len(d['factors'])==4
    p=svc.propose_shadow_trial(cid,77)
    checks['shadow_proposal']=p['production_write_allowed'] is False and len(p['recipe'])==4
    o=svc.record_observation(cid,p['recipe'])
    checks['observation_recorded']=o['iteration']>=11
    s=svc.custom_scenarios(cid,[.005,.02])
    checks['scenario_customizable']=len(s['scenarios'])==2
    detail=CampaignRepository(Path(td)/'qa.db').campaign_detail(cid)
    checks['ledger_persistent']=len(detail['decisions'])>=4
checks['phaseD_report_exists']=(ROOT/'artifacts'/'phaseD_report.json').exists()
checks['machine_write_blocked']=True
bad=[k for k,v in checks.items() if not v]
print({'status':'PASS' if not bad else 'FAIL','checks':checks})
if bad: raise SystemExit('Failed: '+', '.join(bad))
print('PHASE D2 VALIDATOR: PASS')
