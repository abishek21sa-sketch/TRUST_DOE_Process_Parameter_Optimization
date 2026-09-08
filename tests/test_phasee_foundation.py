import json
import pandas as pd
from trustdoe.data_intelligence import inspect_dataset
from trustdoe.multiresponse import weighted_score, pareto_frontier
from trustdoe.model_registry import ModelRegistry
from trustdoe.qualification_report import QualificationReport

def test_dataset_evidence_hash_and_missing(tmp_path):
    p=tmp_path/'x.csv'; pd.DataFrame({'temperature':[1,2,None],'quality':[.8,.9,.7]}).to_csv(p,index=False)
    e=inspect_dataset(p, factor_columns=['temperature'], response_columns=['quality'])
    assert e.dataset_id.startswith('DS-') and e.missing['temperature']==1 and 'no imputation' in e.warnings[0].lower()

def test_multiresponse_weighted_and_pareto():
    x=[[1,7],[2,8],[3,9]]
    assert weighted_score(x,[1,1],[-1,1]).shape==(3,)
    assert set(pareto_frontier(x,[-1,1]).tolist())=={0,1,2}

def test_registry_and_report_are_reproducible(tmp_path):
    m=ModelRegistry(tmp_path/'models').register(response='quality',dataset='DS-1',algorithms_tested=['RSM'],metrics={'rmse':.1},selected_model='RSM',reason='lowest RMSE')
    assert (tmp_path/'models'/(m.model_id+'.json')).exists()
    r=QualificationReport('C1','DS-1',{'temperature':2},{'quality':.9},[],{},[],[],{}, {'state':'HOLD'},[m.evidence_hash])
    r.export(tmp_path/'report'); assert json.loads((tmp_path/'report/process_qualification_report.json').read_text())['campaign']=='C1'
