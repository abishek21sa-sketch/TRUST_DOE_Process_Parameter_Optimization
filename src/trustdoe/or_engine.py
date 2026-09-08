from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.optimize import differential_evolution, milp, Bounds, LinearConstraint
from .domain import ProcessSpace

@dataclass
class RobustRecipe:
    recipe: list[float]
    expected_objective: float
    p95_objective: float
    feasibility_probability: float
    worst_safety_margin: float
    status: str

@dataclass
class BudgetAllocation:
    allocations: list[int]
    total_trials: int
    total_cost: float
    total_information_score: float
    solver_status: str
    solver_message: str


def _scenario_eval(oracle, recipe, perturbations):
    vals=[]; safes=[]
    x=np.asarray(recipe,dtype=float)
    for delta in perturbations:
        xp=np.clip(x+delta,oracle.space.lows,oracle.space.highs)
        o,s=oracle.noiseless(xp); vals.append(o); safes.append(s)
    vals=np.asarray(vals); safes=np.asarray(safes)
    return float(vals.mean()),float(np.quantile(vals,.95)),float(np.mean(safes>=0)),float(safes.min())


def optimize_robust_recipe(oracle, seed:int=2026, n_scenarios:int=120, min_feasibility:float=.99, risk_weight:float=.35) -> RobustRecipe:
    rng=np.random.default_rng(seed)
    scales=(oracle.space.highs-oracle.space.lows)*np.array([.018,.018,.022,.022])
    perturb=rng.normal(0,scales,size=(n_scenarios,oracle.space.dimension))
    bounds=list(zip(oracle.space.lows,oracle.space.highs))
    def penalized(x):
        mean,p95,pfeas,worst=_scenario_eval(oracle,x,perturb)
        penalty=max(0.0,min_feasibility-pfeas)*100 + max(0.0,-worst)*50
        return mean+risk_weight*p95+penalty
    result=differential_evolution(penalized,bounds,seed=seed,popsize=8,maxiter=35,tol=1e-6,polish=True,workers=1)
    mean,p95,pfeas,worst=_scenario_eval(oracle,result.x,perturb)
    status="ROBUST_FEASIBLE" if pfeas>=min_feasibility and worst>=0 else "ROBUST_HOLD"
    return RobustRecipe(result.x.tolist(),mean,p95,pfeas,worst,status)


def pareto_operating_window(oracle, seed:int=2026, n:int=1500) -> list[dict]:
    rng=np.random.default_rng(seed)
    Z=rng.uniform(-1,1,size=(n,oracle.space.dimension)); X=np.array([oracle.space.denormalize(z) for z in Z])
    rows=[]
    for x in X:
        o,s=oracle.noiseless(x)
        # engineered throughput proxy: normalized scan speed * layer thickness / hatch spacing
        throughput=(x[1]/1000.0)*(x[3]/0.04)*(0.10/x[2])
        if s>=0: rows.append({"recipe":x.tolist(),"objective":float(o),"throughput_proxy":float(throughput),"safety_margin":float(s)})
    # Non-dominated: minimize objective, maximize throughput, maximize safety
    frontier=[]
    for i,a in enumerate(rows):
        dominated=False
        for j,b in enumerate(rows):
            if i==j: continue
            weak=(b["objective"]<=a["objective"] and b["throughput_proxy"]>=a["throughput_proxy"] and b["safety_margin"]>=a["safety_margin"])
            strict=(b["objective"]<a["objective"] or b["throughput_proxy"]>a["throughput_proxy"] or b["safety_margin"]>a["safety_margin"])
            if weak and strict: dominated=True; break
        if not dominated: frontier.append(a)
    frontier.sort(key=lambda r:r["objective"])
    return frontier[:80]


def allocate_experiment_budget(info_scores, costs, budget:int, max_replicates:int=3) -> BudgetAllocation:
    info=np.asarray(info_scores,dtype=float); costs=np.asarray(costs,dtype=float)
    if len(info)!=len(costs) or np.any(costs<=0): raise ValueError("Invalid allocation inputs")
    n=len(info)
    # maximize info => minimize negative info. Integer replicate counts.
    c=-info
    constraints=[LinearConstraint(costs[None,:],lb=-np.inf,ub=float(budget))]
    res=milp(c,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.full(n,max_replicates)),constraints=constraints,options={"time_limit":10.0})
    if res.x is None:
        return BudgetAllocation([0]*n,0,0.0,0.0,"INFEASIBLE",str(res.message))
    x=np.rint(res.x).astype(int)
    return BudgetAllocation(x.tolist(),int(x.sum()),float(costs@x),float(info@x),"OPTIMAL" if res.success else "FEASIBLE",str(res.message))


def or_payload(oracle):
    robust=optimize_robust_recipe(oracle)
    frontier=pareto_operating_window(oracle)
    info=[1.0,1.7,2.2,0.9,1.4,2.8]; costs=[1,2,3,1,2,4]
    alloc=allocate_experiment_budget(info,costs,budget=10,max_replicates=2)
    return {"robust_recipe":asdict(robust),"pareto_frontier":frontier,"budget_allocation":asdict(alloc),"formulations":{"robust_nlp":"scenario-based nonlinear optimization with chance-feasibility target","multiobjective":"non-dominated operating-window frontier","integer_allocation":"MILP/HiGHS allocation of finite experiment budget to candidate trials"}}
