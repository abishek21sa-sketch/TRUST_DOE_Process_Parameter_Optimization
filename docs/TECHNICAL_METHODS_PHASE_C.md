# Technical Methods — Phase C

## A. Artificial Intelligence

### Gaussian-process safe experimentation
**Task:** estimate objective and safety response with epistemic uncertainty.  
**Features:** normalized laser power, scan speed, hatch spacing, layer thickness.  
**Targets:** scalar objective and safety margin.  
**Decision use:** TRUST-DOE-S uses posterior mean/uncertainty in constrained next-experiment acquisition.  
**Validation:** synthetic benchmark and automated uncertainty/geometry tests.  
**Limit:** external validation pending.

### Surrogate model laboratory
Phase C quantitatively compares Gaussian Process, Random Forest, Histogram Gradient Boosting, and an interpretable quadratic RSM baseline using identical K-fold splits. RMSE is the primary selection metric; MAE and R² are reported. Complex models are not automatically preferred.

### Drift gate
Two-sample Kolmogorov-Smirnov tests compare baseline and recent campaign segments. A detected shift does not itself prove process drift; it creates a governance requirement to recalibrate/retrain before release.

## B. Industrial Engineering

### Response Surface Methodology
For coded factors `x`, the fitted second-order model is

`y = beta0 + sum beta_i x_i + sum beta_ii x_i^2 + sum beta_ij x_i x_j + epsilon`.

Implementation: `src/trustdoe/process_science.py`.

### ANOVA and lack of fit
Regression, residual, and total sums of squares are computed from the fitted design matrix. When exact replicated design points exist, residual error is decomposed into pure error and lack of fit and an F test is produced.

### Process capability
`Cp = (USL-LSL)/(6 sigma)` and `Cpk = min((USL-mu)/(3 sigma),(mu-LSL)/(3 sigma))` where bilateral specifications exist. One-sided capability is supported for the safety-margin lower limit.

### SPC
Individuals/Moving-Range limits use `sigma_hat = MRbar / 1.128`; three-sigma individual limits provide a monitoring diagnostic rather than causal proof.

### Sensitivity
Central finite differences are converted to normalized factor gradients and local elasticities at the incumbent recipe.

## C. Operations Research

### Robust nonlinear recipe optimization
**Decision variables:** four continuous process parameters.  
**Objective:** minimize expected objective plus a p95 risk penalty.  
**Constraints:** governed parameter bounds, scenario feasibility probability target, nonnegative worst-case sampled safety margin.  
**Method:** scenario-based nonlinear search using differential evolution.  
**Status:** reported as `ROBUST_FEASIBLE` or `ROBUST_HOLD` after independent scenario evaluation.

### Multi-objective operating window
Safe sampled recipes are evaluated on objective, throughput proxy, and safety margin. Non-dominated points form the Pareto operating-window frontier. It is not reduced to a single arbitrary weighted score.

### Experimental-budget MILP
**Decision variables:** integer replicate counts for candidate experiments.  
**Objective:** maximize precomputed marginal information value.  
**Constraint:** total experiment cost <= finite budget.  
**Domains:** bounded nonnegative integers.  
**Solver:** SciPy `milp`, backed by HiGHS.  
**Independent verification:** a mathematical test enumerates a small instance and checks equality with the MILP optimum.
