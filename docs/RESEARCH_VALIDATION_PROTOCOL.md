# Research Validation Protocol — TRUST-DOE Process Parameter Optimization

This protocol implements the attached Research Validation & Benchmarking standard for **TRUST-DOE**.

## Null hypothesis (H0)

H0: TRUST-DOE produces no different recipe than the unconstrained greedy baseline.

The null is not rejected by narrative alone. It is evaluated on a fixed reference scenario and declared seed set `[17, 29, 43]`.

## Baseline, metrics, and ablation

- **Baseline:** unconstrained greedy loss minimization.
- **Primary metrics:** objective value, feasibility, decision change versus baseline, constraint violations, runtime, and reproducibility.
- **Ablation:** remove the trust-region constraint while retaining candidate and safety checks.
- **Sensitivity grid:** tighten the safety threshold and vary trust radius; report recipe feasibility and loss.
- **Expected reporting:** include solver status, selected decision, objective components, scenario/seed, baseline comparison, and any no-feasible result.

## Evidence separation

Observed data are used for context and predictive inputs; simulated data are used for controlled scenario testing; optimized outputs are decisions produced by the signature; shadow-mode results are recommendations without actuation; realized outcomes require a separately identified operational intervention. These classes must not be merged into a single production-performance claim.

## Failure and sensitivity checks

The acceptance suite covers invalid shapes or bounds, an ordinary feasible scenario, the declared ablation, and a deterministic sensitivity call. Any infeasible scenario must return a controlled no-feasible result or a documented validation error rather than silently relaxing a constraint.

## Scalability and external validation boundary

Record candidate/scenario count, runtime, solver status, and optimality gap when a solver is used. Public or synthetic evidence supports analytical validation only. Domain/field validation, prospective shadow mode, and realized intervention outcomes remain separate required stages.
