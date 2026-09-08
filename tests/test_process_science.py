import numpy as np
from trustdoe.process import SyntheticAMOracle
from trustdoe.doe import latin_hypercube
from trustdoe.process_science import QuadraticRSM, lack_of_fit, capability, individuals_spc, local_sensitivity


def test_rsm_recovers_quadratic_signal():
    oracle=SyntheticAMOracle(noise_std=0.0,seed=1)
    rng=np.random.default_rng(1)
    Z=rng.uniform(-1,1,size=(80,oracle.space.dimension))
    X=np.array([oracle.space.denormalize(z) for z in Z])
    # exact quadratic benchmark separate from sinusoidal oracle
    y=1+2*Z[:,0]-0.8*Z[:,1]+0.7*Z[:,0]*Z[:,1]+0.5*Z[:,2]**2
    m=QuadraticRSM(oracle.space).fit(X,y)
    assert m.fit_summary.r2 > .999999
    assert np.max(np.abs(m.predict(X)-y)) < 1e-8


def test_capability_reference_case():
    x=[9.8,10.0,10.2,10.1,9.9,10.05,9.95]
    c=capability(x,lsl=9.0,usl=11.0)
    expected=(11-9)/(6*np.std(x,ddof=1))
    assert abs(c.cp-expected)<1e-12
    assert c.cpk>1


def test_spc_and_sensitivity_are_finite():
    s=individuals_spc([1,1.1,.9,1.05,.98,1.02])
    assert s.ucl>s.center>s.lcl
    oracle=SyntheticAMOracle(noise_std=0)
    x=(oracle.space.lows+oracle.space.highs)/2
    sens=local_sensitivity(oracle.space,lambda r: oracle.noiseless(r)[0],x)
    assert len(sens)==oracle.space.dimension
    assert all(np.isfinite(v.normalized_gradient) for v in sens)


def test_lack_of_fit_available_with_replicates():
    oracle=SyntheticAMOracle(noise_std=0,seed=2)
    rng=np.random.default_rng(2)
    Z=rng.uniform(-1,1,size=(28,4)); X=np.array([oracle.space.denormalize(z) for z in Z])
    X=np.vstack([X,X[:8]])
    y=np.array([oracle.noiseless(r)[0] for r in X]) + rng.normal(0,.002,len(X))
    lof=lack_of_fit(oracle.space,X,y)
    assert lof.available
    assert lof.pure_error_df==8
