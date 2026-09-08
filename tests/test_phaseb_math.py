from __future__ import annotations
import numpy as np
import pytest
from trustdoe.process import SyntheticAMOracle
from trustdoe.campaign import initialize_campaign, run_closed_loop
from trustdoe.calibration import cross_validated_conformal
from trustdoe.acquisition import AcquisitionConfig, optimize_next_experiment
from trustdoe.race import experiment_race
from trustdoe.release import build_release_frontier, release_summary
from trustdoe.ablation import acquisition_ablation


def test_conformal_calibration_is_positive_and_reproducible():
    oracle = SyntheticAMOracle(seed=12)
    state = initialize_campaign(oracle, n_initial=16, seed=12)
    a = cross_validated_conformal(oracle.space, state.observations, "objective", seed=44)
    b = cross_validated_conformal(oracle.space, state.observations, "objective", seed=44)
    assert a.absolute_error_quantile > 0
    assert a == b
    assert a.samples == len(state.observations)


def test_continuous_acquisition_stays_inside_trust_region_and_shadow_only():
    oracle = SyntheticAMOracle(seed=22)
    state = initialize_campaign(oracle, n_initial=16, seed=22)
    cfg = AcquisitionConfig(optimizer_maxiter=12, population_size=6)
    decision, diag = optimize_next_experiment(state, oracle.space, cfg, seed=122)
    assert oracle.space.contains(decision.recipe)
    assert decision.safe_by_model
    assert decision.production_write_allowed is False
    center = oracle.space.normalize(state.incumbent().recipe)
    z = oracle.space.normalize(decision.recipe)
    assert np.linalg.norm(z-center) <= state.trust_radius + 1e-8
    assert diag.objective_calibration.absolute_error_quantile > 0
    assert diag.safety_calibration.absolute_error_quantile > 0


@pytest.mark.slow
def test_experiment_race_contains_distinct_declared_baselines():
    rows = experiment_race(budget=2, seed=123)
    assert {r.strategy for r in rows} == {"TRUST-DOE-S", "RANDOM-LHS", "STATIC-DOE", "UNCONSTRAINED-BO"}
    assert all(len(r.points) == 3 for r in rows)
    assert all(r.production_write_allowed is False for r in rows)


@pytest.mark.slow
def test_release_frontier_has_pareto_point_and_never_enables_machine_write():
    oracle = SyntheticAMOracle(seed=33)
    result = run_closed_loop(oracle, budget=3, seed=33)
    frontier = build_release_frontier(result.state, oracle.space, oracle, n_candidates=18, stress_samples=90, seed=55)
    assert len(frontier) > 0
    assert any(x.pareto_efficient for x in frontier)
    assert all(x.production_write_allowed is False for x in frontier)
    assert all(0 <= x.feasibility_probability <= 1 for x in frontier)
    summary = release_summary(frontier)
    assert summary["production_write_allowed"] is False


@pytest.mark.slow
def test_acquisition_ablation_exposes_four_policy_modes():
    rows = acquisition_ablation(seed=81)
    assert {r.label for r in rows} == {"EXPLOIT", "BALANCED", "LEARN", "LOCAL-CONSERVATIVE"}
    assert all(r.production_write_allowed is False for r in rows)
