# Phase B — Experiment Race and Robust Recipe Release

Phase B preserves the locked Phase A closed-loop engine and adds the first product-grade decision layer.

## Implemented

- Continuous TRUST-DOE-S acquisition optimization in normalized process coordinates.
- Gaussian-process uncertainty augmented by K-fold conformal absolute-residual calibration.
- Experiment Race against Random-LHS, Static DOE and unconstrained Bayesian optimization.
- Acquisition-policy ablation for exploitation, information gain and locality.
- Robust recipe-release frontier with stochastic process drift.
- Explicit release governance: **shadow recommendation only**; autonomous machine writes remain disabled.
- Offline Safe Experiment Cockpit showing the process response landscape, safety boundary, experiment race, robustness frontier and acquisition ablation.

## Evidence status

All Phase B numerical evidence is `SYNTHETIC_VALIDATION`. It is intended to verify computational behavior, mathematical invariants and decision-flow integration. It is not external manufacturing validation.

## Deliberately deferred

- plant/MES/SCADA actuation;
- externally validated additive-manufacturing dataset execution;
- final SvelteKit/Django multi-service product architecture;
- Gemini experiment interrogation;
- final public deployment and V1.0 GitHub cleanup.

These are not represented as implemented.
