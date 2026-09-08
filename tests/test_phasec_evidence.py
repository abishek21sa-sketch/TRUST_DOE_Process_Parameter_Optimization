import pytest
from trustdoe.phasec import build_phasec_evidence

@pytest.mark.slow
def test_phasec_contract(tmp_path):
    p=build_phasec_evidence(tmp_path,seed=2026)
    assert p["version"]=="0.9.0"
    assert p["production_write_allowed"] is False
    assert p["process_science"]["objective_rsm"]["r2"]>0.5
    assert len(p["model_laboratory"]["objective"])>=4
    assert p["operations_research"]["budget_allocation"]["solver_status"] in {"OPTIMAL","FEASIBLE"}
    assert p["data_readiness"]["ready"] is True
    assert (tmp_path/"artifacts"/"phaseC_report.json").exists()
