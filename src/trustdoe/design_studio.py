from __future__ import annotations
import itertools
import numpy as np
from .domain import ProcessSpace
from .doe import latin_hypercube


def full_factorial(space: ProcessSpace, levels: int = 2) -> np.ndarray:
    if levels < 2:
        raise ValueError('levels must be >=2')
    grids = [np.linspace(f.low, f.high, levels) for f in space.factors]
    return np.array(list(itertools.product(*grids)), dtype=float)


def central_composite(space: ProcessSpace, center_reps: int = 6) -> np.ndarray:
    d = space.dimension
    factorial = np.array(list(itertools.product([-1.0, 1.0], repeat=d)), dtype=float)
    axial=[]
    for i in range(d):
        for s in (-1.0,1.0):
            z=np.zeros(d); z[i]=s; axial.append(z)
    z=np.vstack([factorial,np.array(axial),np.zeros((center_reps,d))])
    return np.vstack([space.denormalize(row) for row in z])


def box_behnken(space: ProcessSpace, center_reps: int = 5) -> np.ndarray:
    d=space.dimension
    if d < 3:
        raise ValueError('Box-Behnken requires >=3 factors')
    rows=[]
    for i,j in itertools.combinations(range(d),2):
        for a,b in itertools.product([-1.0,1.0], repeat=2):
            z=np.zeros(d); z[i]=a; z[j]=b; rows.append(z)
    rows.extend([np.zeros(d) for _ in range(center_reps)])
    return np.vstack([space.denormalize(row) for row in np.array(rows)])


def design_metrics(space: ProcessSpace, design: np.ndarray) -> dict:
    X=np.asarray([space.normalize(row) for row in design],dtype=float)
    # linear information matrix incl. intercept, useful for comparison and robust to small designs
    Phi=np.column_stack([np.ones(len(X)),X])
    info=Phi.T@Phi
    sign,logdet=np.linalg.slogdet(info + 1e-12*np.eye(info.shape[0]))
    cond=float(np.linalg.cond(info))
    center=np.mean(X,axis=0)
    radial=np.linalg.norm(X-center,axis=1)
    return {
        'runs':int(len(X)), 'dimension':int(space.dimension),
        'information_logdet':float(logdet if sign>0 else -np.inf),
        'condition_number':cond,
        'mean_radial_coverage':float(np.mean(radial)),
        'max_radial_coverage':float(np.max(radial)),
    }


def design_catalog(space: ProcessSpace, seed: int=2026) -> dict:
    designs={
      'FULL_FACTORIAL_2':full_factorial(space,2),
      'CENTRAL_COMPOSITE':central_composite(space),
      'BOX_BEHNKEN':box_behnken(space),
      'LATIN_HYPERCUBE_24':latin_hypercube(space,24,seed=seed),
    }
    return {name:design_metrics(space,d) for name,d in designs.items()}
