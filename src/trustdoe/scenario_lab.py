from __future__ import annotations
import numpy as np
from .process import SyntheticAMOracle


def stress_recipe(oracle:SyntheticAMOracle, recipe, n:int=3000, seed:int=2026, sigma_fraction:float=0.012)->dict:
    recipe=np.asarray(recipe,dtype=float); rng=np.random.default_rng(seed)
    span=oracle.space.highs-oracle.space.lows
    samples=recipe + rng.normal(0.0,sigma_fraction*span,size=(n,oracle.space.dimension))
    samples=np.clip(samples,oracle.space.lows,oracle.space.highs)
    vals=np.array([oracle.noiseless(x) for x in samples])
    obj=vals[:,0]; safety=vals[:,1]
    return {
      'scenario':'PARAMETER_DRIFT_MONTE_CARLO','samples':n,'seed':seed,'sigma_fraction':sigma_fraction,
      'objective_mean':float(obj.mean()),'objective_p95':float(np.quantile(obj,.95)),
      'objective_p99':float(np.quantile(obj,.99)),
      'safety_p05':float(np.quantile(safety,.05)),'feasibility_probability':float(np.mean(safety>=0)),
    }


def scenario_matrix(oracle:SyntheticAMOracle,recipe)->list[dict]:
    scenarios=[]
    for name,sig in [('NOMINAL_NOISE',.005),('NORMAL_DRIFT',.012),('SEVERE_DRIFT',.025),('QUALIFICATION_STRESS',.04)]:
        r=stress_recipe(oracle,recipe,n=1800,seed=2026+len(scenarios),sigma_fraction=sig); r['name']=name; scenarios.append(r)
    return scenarios
