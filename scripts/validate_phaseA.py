import json
from dataclasses import asdict
import numpy as np
from trustdoe.process import SyntheticAMOracle
from trustdoe.campaign import run_closed_loop
from trustdoe.robustness import stress_recipe
from trustdoe.benchmark import compare_strategies

def main():
    oracle=SyntheticAMOracle(seed=2026)
    res=run_closed_loop(oracle,budget=6,seed=2026)
    inc=res.state.incumbent()
    rob=stress_recipe(oracle,np.array(inc.recipe),n=1500,seed=2026)
    bench=compare_strategies(budget=4,seed=2026)
    checks={
      "shadow_gate": all(not s.decision.production_write_allowed for s in res.steps),
      "recipe_in_bounds": oracle.space.contains(inc.recipe),
      "robust_probability_valid": 0 <= rob.feasibility_probability <= 1,
      "benchmark_has_baseline": any(x.strategy=="RANDOM-LHS" for x in bench),
      "campaign_advanced": len(res.steps)==6,
      "trust_radius_bounded": 0.12 <= res.state.trust_radius <= 1.25,
    }
    payload={"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"incumbent":asdict(inc),"robustness":asdict(rob),"benchmark":[asdict(x) for x in bench]}
    print(json.dumps(payload,indent=2))
    if payload["status"]!="PASS": raise SystemExit(1)
    print("PHASE A VALIDATOR: PASS")
if __name__=="__main__": main()
