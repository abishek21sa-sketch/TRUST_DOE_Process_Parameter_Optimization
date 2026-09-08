from __future__ import annotations
from pathlib import Path
import json
import pytest
from trustdoe.phaseb import build_phaseb_evidence


@pytest.mark.slow
def test_phaseb_evidence_contract(tmp_path: Path):
    p = build_phaseb_evidence(tmp_path, seed=909, quick=True)
    assert p["phase"] == "B"
    assert p["version"] == "0.7.0"
    assert p["evidence_class"] == "SYNTHETIC_VALIDATION"
    assert p["production_write_allowed"] is False
    assert len(p["experiment_race"]) == 4
    assert len(p["release_frontier"]) >= 10
    assert (tmp_path / "artifacts" / "phaseB_report.json").exists()
    assert (tmp_path / "workbench" / "data.json").exists()
    parsed = json.loads((tmp_path / "workbench" / "data.json").read_text())
    assert parsed["governance"]["autonomous_machine_write"] is False
