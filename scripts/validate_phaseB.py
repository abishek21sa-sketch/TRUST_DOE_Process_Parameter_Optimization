from __future__ import annotations
import json
from pathlib import Path

p = json.loads(Path("artifacts/phaseB_report.json").read_text(encoding="utf-8"))
strategies = {r["strategy"] for r in p["experiment_race"]}
checks = {
    "synthetic_evidence_labeled": p["evidence_class"] == "SYNTHETIC_VALIDATION",
    "shadow_gate": p["production_write_allowed"] is False and p["governance"]["autonomous_machine_write"] is False,
    "four_strategy_race": strategies == {"TRUST-DOE-S", "RANDOM-LHS", "STATIC-DOE", "UNCONSTRAINED-BO"},
    "race_has_trajectories": all(len(r["points"]) >= 2 for r in p["experiment_race"]),
    "calibration_positive": p["calibration"]["objective"]["absolute_error_quantile"] > 0 and p["calibration"]["safety"]["absolute_error_quantile"] > 0,
    "release_frontier_present": len(p["release_frontier"]) >= 10 and p["release"]["pareto_count"] >= 1,
    "release_is_shadow_only": p["release"]["production_write_allowed"] is False and p["release"]["recommended"]["production_write_allowed"] is False,
    "surface_grid_present": len(p["surface"]["objective"]) >= 25,
    "ablation_present": len(p["acquisition_ablation"]) == 4,
}
print(json.dumps({"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
print("PHASE B VALIDATOR: PASS")
