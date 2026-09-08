import numpy as np
from trustdoe.process import SyntheticAMOracle
from trustdoe.or_engine import optimize_robust_recipe, allocate_experiment_budget, pareto_operating_window


def test_robust_optimizer_returns_governed_recipe():
    oracle=SyntheticAMOracle(noise_std=0,seed=4)
    r=optimize_robust_recipe(oracle,seed=4,n_scenarios=60,min_feasibility=.95)
    assert oracle.space.contains(r.recipe)
    assert 0<=r.feasibility_probability<=1
    assert r.p95_objective>=r.expected_objective
    assert r.status in {"ROBUST_FEASIBLE","ROBUST_HOLD"}


def test_budget_milp_matches_bruteforce_small_case():
    info=np.array([2.0,3.2,1.1]); costs=np.array([2.0,3.0,1.0]); budget=5
    r=allocate_experiment_budget(info,costs,budget,max_replicates=2)
    best=-1
    for a in range(3):
      for b in range(3):
       for c in range(3):
        if 2*a+3*b+c<=budget: best=max(best,2*a+3.2*b+1.1*c)
    assert abs(r.total_information_score-best)<1e-8
    assert r.total_cost<=budget+1e-9


def test_pareto_frontier_is_safe():
    oracle=SyntheticAMOracle(noise_std=0)
    f=pareto_operating_window(oracle,seed=8,n=220)
    assert f
    assert all(x["safety_margin"]>=0 for x in f)
