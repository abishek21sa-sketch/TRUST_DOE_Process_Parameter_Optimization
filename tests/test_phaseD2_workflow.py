import tempfile
from pathlib import Path
from trustdoe.persistence import CampaignRepository
from trustdoe.workflow import WorkflowService

def test_repository_releases_windows_file_handle():
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'x.db'
        repo=CampaignRepository(p)
        repo.upsert_campaign('C1','test')
        assert repo.list_campaigns()
        p.unlink()  # this is the exact Windows failure mode from Phase D
        assert not p.exists()

def test_interactive_campaign_workflow():
    with tempfile.TemporaryDirectory() as td:
        svc=WorkflowService(Path(td)/'w.db')
        c=svc.create_campaign('interactive',runs=12,seed=4)
        cid=c['campaign']['id']
        assert len(c['observations'])==12
        p=svc.propose_shadow_trial(cid,4)
        assert p['production_write_allowed'] is False
        result=svc.record_observation(cid,p['recipe'])
        assert result['iteration']==13
        scenarios=svc.custom_scenarios(cid,[.005,.01,.03])
        assert len(scenarios['scenarios'])==3
        assert all(0 <= x['feasibility_probability'] <= 1 for x in scenarios['scenarios'])

def test_design_generation_is_governed():
    with tempfile.TemporaryDirectory() as td:
        svc=WorkflowService(Path(td)/'w.db')
        for family in ['FULL_FACTORIAL_2','CENTRAL_COMPOSITE','BOX_BEHNKEN','LATIN_HYPERCUBE']:
            d=svc.generate_design(family,18,8)
            assert d['metrics']['runs']==len(d['rows'])
            assert all(len(r)==4 for r in d['rows'])
