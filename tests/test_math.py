import numpy as np
from trustdoe.process import DEFAULT_SPACE, SyntheticAMOracle
from trustdoe.doe import factorial_points, latin_hypercube, quadratic_features, information_logdet
from trustdoe.domain import CampaignState, Observation
from trustdoe.robustness import stress_recipe

def test_normalization_roundtrip():
    x = np.array([240.0, 1000.0, 0.105, 0.04])
    assert np.allclose(DEFAULT_SPACE.denormalize(DEFAULT_SPACE.normalize(x)), x)

def test_factorial_design_inside_bounds():
    pts = factorial_points(DEFAULT_SPACE)
    assert len(pts) == 2**DEFAULT_SPACE.dimension + 1
    assert all(DEFAULT_SPACE.contains(x) for x in pts)

def test_lhs_reproducible():
    a = latin_hypercube(DEFAULT_SPACE, 10, seed=3)
    b = latin_hypercube(DEFAULT_SPACE, 10, seed=3)
    assert np.allclose(a,b)

def test_quadratic_feature_dimension():
    d=4
    X = quadratic_features(np.zeros((2,d)))
    assert X.shape[1] == 1 + d + d + d*(d-1)//2

def test_information_increases_with_new_geometry():
    z1 = np.zeros((20,4))
    z2 = np.vstack([z1, np.eye(4), -np.eye(4)])
    assert information_logdet(z2) > information_logdet(z1)

def test_campaign_incumbent_safe_only():
    s=CampaignState()
    s.append(Observation((1,2,3,4), 0.1, -0.2))
    s.append(Observation((1,2,3,4), 0.5, 0.2))
    assert s.incumbent().objective == 0.5

def test_robustness_probability_valid():
    oracle=SyntheticAMOracle(seed=2)
    x=np.array([240,1000,.105,.04])
    r=stress_recipe(oracle,x,n=500,seed=2)
    assert 0 <= r.feasibility_probability <= 1
    assert r.objective_p95 >= r.expected_objective
