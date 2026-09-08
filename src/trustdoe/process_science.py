from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Iterable
import numpy as np
from scipy import stats
from .domain import ProcessSpace, Observation


def quadratic_terms(Z: np.ndarray) -> tuple[np.ndarray, list[str]]:
    Z = np.asarray(Z, dtype=float)
    if Z.ndim == 1:
        Z = Z[None, :]
    n, d = Z.shape
    cols = [np.ones(n)]
    names = ["intercept"]
    for i in range(d):
        cols.append(Z[:, i]); names.append(f"x{i+1}")
    for i in range(d):
        cols.append(Z[:, i] ** 2); names.append(f"x{i+1}^2")
    for i in range(d):
        for j in range(i + 1, d):
            cols.append(Z[:, i] * Z[:, j]); names.append(f"x{i+1}:x{j+1}")
    return np.column_stack(cols), names


@dataclass
class RSMFit:
    coefficients: list[float]
    term_names: list[str]
    r2: float
    adjusted_r2: float
    rmse: float
    residual_ss: float
    model_ss: float
    total_ss: float
    df_model: int
    df_residual: int
    f_statistic: float
    f_pvalue: float
    condition_number: float
    max_leverage: float


@dataclass
class LackOfFitResult:
    available: bool
    pure_error_ss: float | None
    lack_of_fit_ss: float | None
    pure_error_df: int | None
    lack_of_fit_df: int | None
    f_statistic: float | None
    p_value: float | None


class QuadraticRSM:
    def __init__(self, space: ProcessSpace):
        self.space = space
        self.beta: np.ndarray | None = None
        self.names: list[str] = []
        self.fit_summary: RSMFit | None = None

    def fit(self, recipes: np.ndarray, y: np.ndarray) -> "QuadraticRSM":
        X_phys = np.asarray(recipes, dtype=float)
        y = np.asarray(y, dtype=float)
        Z = np.array([self.space.normalize(r) for r in X_phys])
        X, names = quadratic_terms(Z)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred = X @ beta
        resid = y - pred
        ss_res = float(np.sum(resid ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        ss_model = max(0.0, ss_tot - ss_res)
        n, p = X.shape
        df_model = max(1, p - 1)
        df_resid = max(1, n - p)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
        adj = 1.0 - (1.0-r2)*(n-1)/df_resid if n > p else r2
        mse_model = ss_model / df_model
        mse_resid = ss_res / df_resid
        f = mse_model / mse_resid if mse_resid > 0 else np.inf
        pval = float(stats.f.sf(f, df_model, df_resid)) if np.isfinite(f) else 0.0
        h = X @ np.linalg.pinv(X.T @ X) @ X.T
        self.beta = beta
        self.names = names
        self.fit_summary = RSMFit(
            coefficients=beta.tolist(), term_names=names, r2=float(r2), adjusted_r2=float(adj),
            rmse=float(np.sqrt(ss_res/max(1,n))), residual_ss=ss_res, model_ss=ss_model,
            total_ss=ss_tot, df_model=df_model, df_residual=df_resid, f_statistic=float(f),
            f_pvalue=pval, condition_number=float(np.linalg.cond(X)),
            max_leverage=float(np.max(np.diag(h))),
        )
        return self

    def predict(self, recipes: np.ndarray) -> np.ndarray:
        if self.beta is None:
            raise RuntimeError("RSM not fitted")
        recipes = np.atleast_2d(np.asarray(recipes, dtype=float))
        Z = np.array([self.space.normalize(r) for r in recipes])
        X, _ = quadratic_terms(Z)
        return X @ self.beta


def lack_of_fit(space: ProcessSpace, recipes: np.ndarray, y: np.ndarray, decimals: int = 10) -> LackOfFitResult:
    recipes = np.asarray(recipes, dtype=float)
    y = np.asarray(y, dtype=float)
    model = QuadraticRSM(space).fit(recipes, y)
    keys = [tuple(np.round(space.normalize(r), decimals)) for r in recipes]
    groups: dict[tuple[float, ...], list[float]] = {}
    for k, yi in zip(keys, y): groups.setdefault(k, []).append(float(yi))
    pe_ss = 0.0; pe_df = 0
    for vals in groups.values():
        if len(vals) > 1:
            arr = np.asarray(vals); pe_ss += float(np.sum((arr-arr.mean())**2)); pe_df += len(vals)-1
    unique = len(groups)
    p = len(model.fit_summary.coefficients)
    lof_df = unique - p
    if pe_df <= 0 or lof_df <= 0:
        return LackOfFitResult(False, None, None, None, None, None, None)
    lof_ss = max(0.0, model.fit_summary.residual_ss - pe_ss)
    ms_lof = lof_ss / lof_df
    ms_pe = pe_ss / pe_df
    f = ms_lof / ms_pe if ms_pe > 0 else np.inf
    pval = float(stats.f.sf(f, lof_df, pe_df)) if np.isfinite(f) else 0.0
    return LackOfFitResult(True, pe_ss, lof_ss, pe_df, lof_df, float(f), pval)


@dataclass
class CapabilityResult:
    mean: float
    std: float
    cp: float | None
    cpk: float | None
    cpu: float | None
    cpl: float | None
    n: int


def capability(values: Iterable[float], lsl: float | None = None, usl: float | None = None) -> CapabilityResult:
    x = np.asarray(list(values), dtype=float)
    if x.size < 2: raise ValueError("Capability requires >=2 observations")
    mean = float(np.mean(x)); std = float(np.std(x, ddof=1))
    if std <= 0:
        cpu = cpl = cp = cpk = float("inf")
    else:
        cpu = (usl-mean)/(3*std) if usl is not None else None
        cpl = (mean-lsl)/(3*std) if lsl is not None else None
        cp = (usl-lsl)/(6*std) if usl is not None and lsl is not None else None
        vals = [v for v in [cpu,cpl] if v is not None]
        cpk = min(vals) if vals else None
    return CapabilityResult(mean,std,cp,cpk,cpu,cpl,int(x.size))


@dataclass
class SPCResult:
    center: float
    sigma: float
    ucl: float
    lcl: float
    violations: list[int]
    moving_range_bar: float


def individuals_spc(values: Iterable[float]) -> SPCResult:
    x = np.asarray(list(values), dtype=float)
    if x.size < 3: raise ValueError("SPC requires >=3 observations")
    mr = np.abs(np.diff(x)); mrbar = float(np.mean(mr))
    sigma = mrbar / 1.128 if mrbar > 0 else 0.0
    center = float(np.mean(x)); ucl=center+3*sigma; lcl=center-3*sigma
    violations = np.flatnonzero((x>ucl)|(x<lcl)).astype(int).tolist()
    return SPCResult(center,sigma,ucl,lcl,violations,mrbar)


@dataclass
class SensitivityResult:
    factor: str
    normalized_gradient: float
    elasticity: float


def local_sensitivity(space: ProcessSpace, fn, recipe: Iterable[float], step_fraction: float = 0.01) -> list[SensitivityResult]:
    x = np.asarray(list(recipe), dtype=float)
    base = float(fn(x))
    out=[]
    for i,f in enumerate(space.factors):
        h=(f.high-f.low)*step_fraction
        xp=x.copy(); xm=x.copy(); xp[i]=min(f.high,x[i]+h); xm[i]=max(f.low,x[i]-h)
        grad=(float(fn(xp))-float(fn(xm)))/(xp[i]-xm[i])
        normalized=grad*(f.high-f.low)/2
        elasticity=(grad*x[i]/base) if abs(base)>1e-12 else 0.0
        out.append(SensitivityResult(f.name,float(normalized),float(elasticity)))
    return out


def process_science_payload(space: ProcessSpace, observations: list[Observation]) -> dict:
    X=np.array([o.recipe for o in observations],dtype=float)
    obj=np.array([o.objective for o in observations])
    safety=np.array([o.safety_margin for o in observations])
    rsm_obj=QuadraticRSM(space).fit(X,obj)
    rsm_safe=QuadraticRSM(space).fit(X,safety)
    return {
        "objective_rsm": asdict(rsm_obj.fit_summary),
        "safety_rsm": asdict(rsm_safe.fit_summary),
        "objective_lack_of_fit": asdict(lack_of_fit(space,X,obj)),
        "objective_spc": asdict(individuals_spc(obj)),
        "safety_capability": asdict(capability(safety, lsl=0.0)),
    }
