from __future__ import annotations
import json
from trustdoe.phaseb import build_phaseb_evidence

p = build_phaseb_evidence(".")
print(json.dumps({
    "phase": p["phase"],
    "version": p["version"],
    "evidence_class": p["evidence_class"],
    "production_write_allowed": p["production_write_allowed"],
    "race": [{"strategy": r["strategy"], "best": r["final_best_safe_objective"], "unsafe": r["unsafe_trials"]} for r in p["experiment_race"]],
    "release": p["release"],
}, indent=2))
print("PHASE B EVIDENCE BUILD: PASS")
