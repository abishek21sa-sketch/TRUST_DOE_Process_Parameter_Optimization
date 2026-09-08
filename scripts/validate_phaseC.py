from pathlib import Path
import json, math
root=Path(__file__).resolve().parents[1]
p=json.loads((root/"artifacts"/"phaseC_report.json").read_text(encoding="utf-8"))
checks={
 "shadow_gate": p["production_write_allowed"] is False,
 "data_ready": p["data_readiness"]["ready"] is True,
 "rsm_finite": math.isfinite(p["process_science"]["objective_rsm"]["r2"]),
 "model_baseline_present": any(x["model"]=="QuadraticRSM" for x in p["model_laboratory"]["objective"]),
 "multiple_models_compared": len(p["model_laboratory"]["objective"])>=4,
 "robust_recipe_in_probability_domain": 0<=p["operations_research"]["robust_recipe"]["feasibility_probability"]<=1,
 "pareto_frontier_nonempty": len(p["operations_research"]["pareto_frontier"])>0,
 "milp_budget_feasible": p["operations_research"]["budget_allocation"]["total_cost"]<=10+1e-9,
 "milp_status_valid": p["operations_research"]["budget_allocation"]["solver_status"] in ["OPTIMAL","FEASIBLE"],
 "external_validation_honest": p["governance"]["real_world_validation"]=="PENDING",
}
print(json.dumps({"status":"PASS" if all(checks.values()) else "FAIL","checks":checks},indent=2))
if not all(checks.values()): raise SystemExit(1)
print("PHASE C VALIDATOR: PASS")
