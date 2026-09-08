from pathlib import Path
import tempfile
import numpy as np
from trustdoe.process import DEFAULT_SPACE, SyntheticAMOracle
from trustdoe.design_studio import full_factorial, central_composite, box_behnken, design_catalog
from trustdoe.persistence import CampaignRepository
from trustdoe.domain import Observation
from trustdoe.scenario_lab import stress_recipe, scenario_matrix
from trustdoe.qualification import qualification_gate
from trustdoe.data_gateway import inspect_csv, public_source_manifest


def test_design_studio_catalog_and_bounds():
    for d in [full_factorial(DEFAULT_SPACE), central_composite(DEFAULT_SPACE), box_behnken(DEFAULT_SPACE)]:
        assert d.shape[1] == DEFAULT_SPACE.dimension
        assert np.all(d >= DEFAULT_SPACE.lows) and np.all(d <= DEFAULT_SPACE.highs)
    cat=design_catalog(DEFAULT_SPACE)
    assert len(cat)==4
    assert all(v['runs']>0 for v in cat.values())


def test_design_information_is_finite():
    cat=design_catalog(DEFAULT_SPACE)
    assert all(np.isfinite(v['information_logdet']) for v in cat.values())
    assert all(v['condition_number']>0 for v in cat.values())


def test_campaign_repository_persists_and_hashes():
    with tempfile.TemporaryDirectory() as td:
        repo=CampaignRepository(Path(td)/'x.db')
        repo.upsert_campaign('C1','test')
        obs=Observation((200,900,.1,.04),.3,.8)
        repo.append_observation('C1',1,obs)
        h=repo.record_decision('C1','TEST',{'a':1})
        d=repo.campaign_detail('C1')
        assert len(h)==64 and len(d['observations'])==1 and len(d['decisions'])==1


def test_scenario_lab_reproducible_and_probability_valid():
    o=SyntheticAMOracle(seed=4); recipe=np.array([240,1000,.105,.04])
    a=stress_recipe(o,recipe,n=500,seed=9); b=stress_recipe(o,recipe,n=500,seed=9)
    assert a==b
    assert 0 <= a['feasibility_probability'] <= 1
    assert a['objective_p99'] >= a['objective_p95']
    assert len(scenario_matrix(o,recipe))==4


def test_qualification_gate_never_machine_writes():
    q=qualification_gate(feasibility_probability=1,safety_p05=.5,evidence_class='SYNTHETIC_VALIDATION',data_ready=True,model_validated=True)
    assert q['state']=='QUALIFIED_SHADOW_RECIPE' and q['production_write_allowed'] is False
    q2=qualification_gate(feasibility_probability=.8,safety_p05=-.1,evidence_class='EXTERNAL_VALIDATION',data_ready=True,model_validated=True)
    assert q2['state']=='HOLD_FOR_MORE_EVIDENCE'


def test_data_gateway_refuses_missing_fields(tmp_path):
    p=tmp_path/'bad.csv'; p.write_text('laser_power,objective\n200,0.2\n')
    r=inspect_csv(p)
    assert not r['ready'] and 'scan_speed' in r['missing_fields']
    assert public_source_manifest()[0]['validation']=='EXTERNAL_DATASET_EXECUTION_PENDING'
