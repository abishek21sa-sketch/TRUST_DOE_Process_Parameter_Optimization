# Technical Methods — Phase A Closed-Loop Engine

## A. Artificial Intelligence

### Gaussian-process process surrogates
**Task:** estimate process objective and safety margin from sparse experiments.  
**Inputs:** governed process recipe variables in normalized [-1,1] coordinates.  
**Targets:** scalar objective (lower is better) and scalar safety margin (>=0 feasible).  
**Model:** GaussianProcessRegressor with Matern-5/2 covariance and learned noise term.  
**Training:** refit on all campaign observations after each new experiment.  
**Inference:** posterior mean and standard deviation for candidate recipes.  
**Baseline:** random Latin-hypercube experimentation; future phase adds static DOE and unconstrained-optimum baselines.  
**Uncertainty:** GP posterior standard deviation; Phase A uses a conservative beta multiplier for shadow selection and does not claim calibrated real-world coverage.  
**Decision use:** objective upper confidence bound and safety lower confidence bound feed the next-experiment controller.  
**Evidence:** SYNTHETIC_VALIDATION only.

### TRUST-DOE-S adaptive experimentation
Candidate j is eligible only inside the normalized trust radius and when its conservative safety lower bound is non-negative. For minimization:

`I_j^L = max(0, f_inc - (mu_f,j + beta sigma_f,j))`

D-optimal information gain is computed as the log-determinant increment of the quadratic response-surface information matrix. The score is:

`S_j = lambda_I I_j^L + lambda_G G_j - lambda_D ||x_j-x_c||_2`

The chosen output is always a **shadow experiment**. `production_write_allowed=False` is a code invariant.

## B. Industrial Engineering

### Design of Experiments
Latin-hypercube and factorial designs are executable. The quadratic response-surface feature basis contains intercept, linear effects, squared effects and two-factor interactions. Information geometry is quantified using `log det(X'X)` with a numerical ridge only for stable determinant evaluation.

### Response Surface / process window
Recipes are normalized by physical lower/upper bounds. A separate modeled safety margin defines the current feasible process window. The trust region limits extrapolation from the best observed safe recipe.

### Sequential experiment governance
The scarce IE resource is **physical experiment budget**. Each new trial must provide either conservative predicted improvement or information value while respecting the modeled safe region.

## C. Operations Research

### Constrained sequential selection
**Decision variable:** one next recipe x chosen from a generated candidate set.  
**Objective:** maximize conservative improvement + information gain - extrapolation distance.  
**Constraints:** physical bounds, trust-region distance, conservative safety lower bound.  
**Domain:** continuous process settings represented by a dense candidate approximation in Phase A.  
**Solver:** finite candidate evaluation; Phase B will add continuous acquisition optimization and multi-objective recipe release.  
**Status:** a result is emitted only when at least one eligible candidate exists; otherwise the controller fails closed or deliberately relaxes only the shadow search confidence setting.  
**Validation:** tests independently assert trust-region, bounds, safety and no-production-write invariants.

---

# Phase B Addendum

## Artificial Intelligence — calibrated sequential learning

**Task:** estimate objective and safety surfaces from a small sequential experiment campaign and choose the next informative safe experiment.

**Inputs/features:** normalized process parameters: laser power, scan speed, hatch spacing, layer thickness.

**Targets:** scalar process objective and scalar safety margin.

**Model:** Gaussian Process Regression with Matern-2.5 covariance and white-noise term.

**Training:** refit to all currently observed campaign data after each adaptive iteration.

**Uncertainty:** GP predictive standard deviation plus K-fold conformal absolute-residual radius. The safety gate uses the more conservative of the parametric and conformal widths.

**Baseline:** random Latin-hypercube experimentation, static DOE, and unconstrained Bayesian optimization.

**Decision use:** the model does not directly issue machine settings. It parameterizes a constrained next-experiment optimization.

**Validation:** synthetic benchmark only; no factory accuracy claim.

## Industrial Engineering — sequential DOE and information geometry

For normalized design vector `z`, the quadratic response-surface basis contains intercept, first-order, squared and pairwise-interaction terms. The experimental information matrix is

`M = X^T X + εI`.

D-optimal information utility is measured through incremental log determinant

`ΔI = log det(M + φφ^T) - log det(M)`.

Implementation: `src/trustdoe/doe.py`, `src/trustdoe/acquisition.py`.

Operational interpretation: a candidate can be valuable because it improves the current process objective, because it increases what is known about the local response surface, or both.

## Operations Research — continuous safe acquisition

Decision variable: continuous normalized recipe `z ∈ [-1,1]^d`.

Objective:

`max λ_imp * conservative_improvement + λ_info * information_gain - λ_dist * distance`.

Constraints:

1. governed factor bounds;
2. adaptive Euclidean trust region around the incumbent;
3. calibrated conservative safety lower bound >= 0;
4. production-write flag is always false.

Solver: SciPy differential evolution with deterministic seed and local polishing.

Independent checks: bounds, trust-region distance, model-safety gate, shadow-write invariant, and benchmark comparison.

## Simulation / uncertainty — robust recipe release

Each recipe is perturbed by Gaussian process-input drift scaled to factor range. The synthetic process oracle is evaluated over repeated samples to estimate expected objective, p95 objective and feasibility probability. These quantities are explicitly labeled simulated/synthetic and are not realized production outcomes.

# Phase D Product Engineering Addendum

## Artificial Intelligence
Phase D retains the validated Phase A–C surrogate and safe experimentation engines. Model selection remains quantitative and benchmarked against an interpretable quadratic RSM baseline. The product does not use an LLM as a decision engine.

## Industrial Engineering
The Experiment Design Studio implements multiple DOE families and compares their information geometry. Operating-window qualification uses coded/physical parameter transformations, process-response models, capability/SPC evidence, and sensitivity rather than presenting a single unconstrained optimum.

## Operations Research
The Recipe Forge separates two decision classes: continuous robust recipe search and discrete experimental-resource allocation. The latter has explicit integer allocations, a finite budget constraint, solver status, and an independent brute-force test oracle on the small verification instance.

## Persistence and governance
Campaign observations and decisions are persisted in SQLite. Decision payloads are SHA-256 hashed in the ledger. All qualification states preserve `production_write_allowed = false`; external plant governance is outside the software boundary.
