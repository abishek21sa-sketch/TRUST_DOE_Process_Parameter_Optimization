import pandas as pd
import numpy as np
from trustdoe.process import SyntheticAMOracle
from trustdoe.campaign import run_closed_loop
from trustdoe.model_lab import benchmark_models
from trustdoe.readiness import assess_frame
from trustdoe.drift import detect_drift


def _campaign():
    o=SyntheticAMOracle(seed=12)
    return o, run_closed_loop(o,budget=14,seed=12).state.observations


def test_model_lab_has_interpretable_baseline_and_ml():
    oracle,obs=_campaign(); s=benchmark_models(oracle.space,obs,"objective",seed=1)
    names={x.model for x in s}
    assert "QuadraticRSM" in names and "GaussianProcess" in names
    assert all(np.isfinite(x.rmse) for x in s)


def test_readiness_refuses_missing_fields():
    bad=pd.DataFrame({"laser_power":[1]*20})
    r=assess_frame(bad)
    assert not r.ready and "objective" in r.missing_columns


def test_readiness_accepts_complete_frame():
    oracle,obs=_campaign()
    df=pd.DataFrame([{**{f.name:v for f,v in zip(oracle.space.factors,o.recipe)},"objective":o.objective,"safety_margin":o.safety_margin} for o in obs])
    assert assess_frame(df).ready


def test_drift_returns_named_signals():
    oracle,obs=_campaign(); s=detect_drift(oracle.space,obs)
    assert s
    assert {x.variable for x in s}.issuperset({"objective_residual","safety_residual"})
    assert any(x.signal_class=="DESIGN_DISTRIBUTION_SHIFT" for x in s)
    assert any(x.signal_class=="PROCESS_RESIDUAL_SHIFT" for x in s)
