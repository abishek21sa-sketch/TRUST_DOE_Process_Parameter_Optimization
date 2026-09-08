from pathlib import Path
import pandas as pd
from trustdoe.process import DEFAULT_SPACE
from trustdoe.data_adapter import ingest_experiment_csv
from trustdoe.benchmark import compare_strategies

def test_csv_ingestion_hash_and_evidence(tmp_path: Path):
    rows=[]
    for i in range(6):
        rows.append({"laser_power":200+i,"scan_speed":800+i*5,"hatch_spacing":.09,"layer_thickness":.04,"objective":1.0,"safety_margin":.2})
    p=tmp_path/"exp.csv"
    pd.DataFrame(rows).to_csv(p,index=False)
    obs, report=ingest_experiment_csv(p,DEFAULT_SPACE)
    assert report.rows==6 and len(report.sha256)==64
    assert all(o.source=="USER_SUPPLIED_HISTORICAL" for o in obs)

def test_csv_rejects_missing_fields(tmp_path: Path):
    p=tmp_path/"bad.csv"
    pd.DataFrame([{"laser_power":200}]).to_csv(p,index=False)
    try:
        ingest_experiment_csv(p,DEFAULT_SPACE)
    except ValueError as e:
        assert "Missing required columns" in str(e)
    else:
        raise AssertionError("Expected validation error")

def test_benchmark_returns_fair_declared_strategies():
    rows=compare_strategies(budget=2,seed=15)
    assert {r.strategy for r in rows}=={"TRUST-DOE","RANDOM-LHS"}
    assert all(r.trials==16 for r in rows)
