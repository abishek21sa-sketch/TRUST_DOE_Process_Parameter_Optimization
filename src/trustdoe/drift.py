from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.stats import ks_2samp
from .domain import ProcessSpace, Observation
from .process_science import QuadraticRSM

@dataclass
class DriftSignal:
    variable: str
    statistic: float
    p_value: float
    drift: bool
    signal_class: str


def _ks(name, a, b, alpha, signal_class):
    r=ks_2samp(np.asarray(a),np.asarray(b),method="auto")
    return DriftSignal(name,float(r.statistic),float(r.pvalue),bool(r.pvalue<alpha),signal_class)


def detect_drift(space: ProcessSpace, observations: list[Observation], recent_fraction: float=0.35, alpha: float=0.05) -> list[DriftSignal]:
    """Separate deliberate experimental-design shift from response-residual drift.

    Adaptive experimentation intentionally changes the recipe distribution, so a KS shift in
    factor values is *not* treated as evidence of process drift. Process drift is suspected only
    when recent response residuals materially depart from the baseline model residual distribution.
    """
    n=len(observations); split=max(12,int(n*(1-recent_fraction)))
    if n-split < 5 or split < 12: return []
    X=np.array([o.recipe for o in observations],dtype=float)
    obj=np.array([o.objective for o in observations],dtype=float)
    safe=np.array([o.safety_margin for o in observations],dtype=float)
    out=[]
    for i,f in enumerate(space.factors):
        out.append(_ks(f.name,X[:split,i],X[split:,i],alpha,"DESIGN_DISTRIBUTION_SHIFT"))
    # Fit on baseline only; compare baseline vs recent residual distributions.
    for name,y in [("objective_residual",obj),("safety_residual",safe)]:
        model=QuadraticRSM(space).fit(X[:split],y[:split])
        base_res=y[:split]-model.predict(X[:split])
        recent_res=y[split:]-model.predict(X[split:])
        out.append(_ks(name,base_res,recent_res,alpha,"PROCESS_RESIDUAL_SHIFT"))
    return out


def drift_payload(space,obs):
    sig=detect_drift(space,obs)
    process=[s for s in sig if s.signal_class=="PROCESS_RESIDUAL_SHIFT"]
    design=[s for s in sig if s.signal_class=="DESIGN_DISTRIBUTION_SHIFT"]
    return {
      "signals":[asdict(s) for s in sig],
      "design_shift_detected":any(s.drift for s in design),
      "process_drift_suspected":any(s.drift for s in process),
      "method":"KS monitoring with explicit separation of adaptive-design shift and model-residual shift",
      "action":"Design-distribution shift is expected under active learning. Only residual shift opens a recalibration/retraining governance gate; it does not by itself prove causal process drift."
    }
