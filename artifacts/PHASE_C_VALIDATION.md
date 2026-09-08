# Phase C Validation Evidence

**Evidence class:** SYNTHETIC_VALIDATION  
**Version:** 0.9.0  
**Machine write:** BLOCKED

## Release gates
- Fast automated suite: **27 passed, 5 slow tests deselected**.
- Dedicated Phase C evidence build: **PASS**.
- Phase C governance/invariant validator: **PASS**.
- Source compilation: **PASS**.

## Process science
- Objective RSM in-sample R²: **0.9982**.
- Adjusted R²: **0.9963**.
- The high in-sample R² is not promoted to predictive accuracy; cross-validation is reported separately.

## Model laboratory — objective cross-validation
- GaussianProcess: RMSE 0.3115, MAE 0.1960, R² 0.4862.
- RandomForest: RMSE 0.3521, MAE 0.2604, R² 0.3435.
- HistGradientBoosting: RMSE 0.4695, MAE 0.4109, R² -0.1673.
- QuadraticRSM: RMSE 0.5691, MAE 0.2949, R² -0.7149.

Selected model by declared rule: **GaussianProcess**.

## Operations Research
- Robust nonlinear recipe status: **ROBUST_FEASIBLE**.
- Sampled feasibility probability: **1.000**.
- Worst sampled safety margin: **0.9777**.
- Pareto operating-window points retained: **59**.
- Integer experiment-budget allocation solver status: **OPTIMAL**.
- Allocated cost: **10.0 / 10.0**.
- MILP is independently checked against brute-force enumeration on a small test instance.

## Interpretation boundary
These are controlled synthetic-benchmark results. They establish computational correctness and reproducibility, not factory performance, causal benefit, or production readiness. External validation remains PENDING.
