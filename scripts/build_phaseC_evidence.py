from pathlib import Path
from trustdoe.phasec import build_phasec_evidence
p=build_phasec_evidence(Path(__file__).resolve().parents[1],seed=2026)
print("PHASE C EVIDENCE BUILD: PASS")
print("Selected objective model:",p["model_laboratory"]["selected"]["objective"])
print("Objective RSM R2:",round(p["process_science"]["objective_rsm"]["r2"],4))
print("Robust recipe status:",p["operations_research"]["robust_recipe"]["status"])
print("MILP allocation status:",p["operations_research"]["budget_allocation"]["solver_status"])
