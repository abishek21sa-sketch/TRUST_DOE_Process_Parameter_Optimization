import numpy as np
from trustdoe.process import SyntheticAMOracle
from trustdoe.campaign import initialize_campaign, candidate_pool, run_closed_loop
from trustdoe.surrogate import GPSurrogate
from trustdoe.controller import select_next_experiment, adapt_trust_region

def test_gp_fits_and_predicts_uncertainty():
    oracle=SyntheticAMOracle(seed=4)
    state=initialize_campaign(oracle,n_initial=16,seed=4)
    gp=GPSurrogate(oracle.space).fit(state.observations,"objective")
    p=gp.predict(np.array([state.incumbent().recipe]))
    assert np.isfinite(p.mean[0]) and p.std[0] > 0

def test_next_experiment_is_shadow_and_in_trust_region():
    oracle=SyntheticAMOracle(seed=5)
    state=initialize_campaign(oracle,n_initial=18,seed=5)
    d=select_next_experiment(state,oracle.space,candidate_pool(oracle.space,1200,44),beta=1.28)
    assert d.production_write_allowed is False
    assert d.safe_by_model
    assert d.normalized_distance <= state.trust_radius + 1e-9

def test_unsafe_observation_shrinks_trust_region():
    oracle=SyntheticAMOracle(seed=5)
    state=initialize_campaign(oracle,n_initial=18,seed=5)
    d=select_next_experiment(state,oracle.space,candidate_pool(oracle.space,1000,47),beta=1.28)
    old=state.trust_radius
    adapt_trust_region(state,state.incumbent().objective,d,d.predicted_objective,False)
    assert state.trust_radius < old

def test_closed_loop_adds_budget_trials():
    oracle=SyntheticAMOracle(seed=8)
    res=run_closed_loop(oracle,budget=3,seed=8)
    assert len(res.steps)==3
    assert len(res.state.observations)==17
    assert all(not s.decision.production_write_allowed for s in res.steps)
