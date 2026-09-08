from __future__ import annotations
from dataclasses import dataclass, asdict
import warnings
import numpy as np
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel
from sklearn.exceptions import ConvergenceWarning
from .domain import ProcessSpace, Observation
from .process_science import QuadraticRSM

@dataclass
class ModelScore:
    model: str
    rmse: float
    mae: float
    r2: float
    complexity_class: str


def _normalized(space, observations):
    return np.array([space.normalize(o.recipe) for o in observations])

def benchmark_models(space: ProcessSpace, observations: list[Observation], target: str="objective", seed: int=2026) -> list[ModelScore]:
    if len(observations) < 12: raise ValueError("Need >=12 observations for model benchmark")
    X=_normalized(space,observations); y=np.array([getattr(o,target) for o in observations],dtype=float)
    folds=3; cv=KFold(n_splits=folds,shuffle=True,random_state=seed)
    models={
      "GaussianProcess": GaussianProcessRegressor(kernel=ConstantKernel(1.0)*Matern(length_scale=np.ones(space.dimension),nu=2.5)+WhiteKernel(1e-4),normalize_y=True,random_state=seed,n_restarts_optimizer=0),
      "RandomForest": RandomForestRegressor(n_estimators=90,min_samples_leaf=2,random_state=seed,n_jobs=1),
      "HistGradientBoosting": HistGradientBoostingRegressor(max_iter=100,l2_regularization=0.03,random_state=seed),
    }
    scores=[]
    for name,model in models.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",ConvergenceWarning)
            pred=cross_val_predict(model,X,y,cv=cv,n_jobs=1)
        scores.append(ModelScore(name,float(np.sqrt(mean_squared_error(y,pred))),float(mean_absolute_error(y,pred)),float(r2_score(y,pred)),"NONLINEAR_ML"))
    # RSM out-of-fold manually in physical coordinates
    recipes=np.array([o.recipe for o in observations],dtype=float); pred=np.zeros_like(y)
    for tr,te in cv.split(recipes): pred[te]=QuadraticRSM(space).fit(recipes[tr],y[tr]).predict(recipes[te])
    scores.append(ModelScore("QuadraticRSM",float(np.sqrt(mean_squared_error(y,pred))),float(mean_absolute_error(y,pred)),float(r2_score(y,pred)),"STATISTICAL_BASELINE"))
    return sorted(scores,key=lambda s:s.rmse)

def model_lab_payload(space,observations):
    obj=benchmark_models(space,observations,"objective")
    safe=benchmark_models(space,observations,"safety_margin",seed=2027)
    return {"objective":[asdict(x) for x in obj],"safety":[asdict(x) for x in safe],"selected":{"objective":obj[0].model,"safety":safe[0].model},"selection_rule":"lowest cross-validated RMSE; RSM retained as interpretable baseline"}
