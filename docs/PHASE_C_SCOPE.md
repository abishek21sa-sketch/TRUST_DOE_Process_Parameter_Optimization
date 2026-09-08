# Phase C — Process Science + Decision Engineering

Phase C turns the Phase B safe-experiment kernel into a deeper engineering decision system. It deliberately prioritizes computational depth over frontend expansion.

## Added in Phase C
- second-order coded response-surface engine implemented directly from the design matrix;
- model/regression ANOVA statistics and leverage/conditioning diagnostics;
- pure-error vs lack-of-fit decomposition when replicated trials exist;
- Individuals/Moving-Range statistical process control;
- Cp/Cpk/Cpu/Cpl process-capability calculations;
- finite-difference normalized sensitivity/elasticity;
- model laboratory comparing Gaussian Process, Random Forest, Histogram Gradient Boosting, and quadratic RSM baseline using cross-validation;
- two-sample KS drift/readiness gate;
- scenario-based nonlinear robust recipe optimization;
- multi-objective non-dominated operating-window frontier;
- integer experimental-budget allocation MILP solved through SciPy/HiGHS;
- canonical external-data readiness contract;
- reproducible evidence artifact and mathematical oracle tests.

## Still intentionally outside Phase C
- factory-connected control or machine writes;
- claims of real-world predictive accuracy;
- direct NIST AM Bench download/execution;
- multi-user enterprise persistence and auth;
- final SvelteKit/Django/PostgreSQL product shell;
- external Gemini reasoning layer.

Those belong to the final product phase because this release first establishes the engineering core they will consume.
