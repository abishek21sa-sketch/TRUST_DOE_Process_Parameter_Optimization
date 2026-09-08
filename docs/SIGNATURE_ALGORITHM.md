# TRUST-DOE — Signature Algorithm Contract

This document is the project-native mathematical center required by the portfolio governance pack. The implementation alias is **SAFE-TRUST recipe selection**.

## Operational decision

The module makes one operational decision: **select a process recipe inside a trust region with a minimum predicted safety score**.

## Mathematical center

- **Decision variables:** continuous or discretized recipe vector and predicted safety score.
- **Objective:** minimize predicted recipe loss among feasible candidates.
- **Constraints and release gates:** distance from the trust center <= trust radius; predicted safety >= minimum safety.
- **Determinism:** the reference contract is deterministic for a fixed candidate set, scenario, and seed.
- **Solver status:** the current reference is an executable enumerative/closed-form contract; production solver integration remains downstream of this gate.

## Baseline and counterfactual

The named baseline is **unconstrained greedy loss minimization**. The counterfactual is evaluated on the same inputs and scenario so that a claimed improvement cannot be caused by a changed data slice.

## Ablation

The declared ablation is to **remove the trust-region constraint while retaining candidate and safety checks**. It is executable through the module's `ablation(...)` function and is covered by the signature tests.

## Sensitivity

The sensitivity sweep is: **tighten the safety threshold and vary trust radius; report recipe feasibility and loss**. Sensitivity output is evidence about robustness, not a claim of causal production impact.

## Evidence classes and authority

Evidence is kept separate as observed, simulated, optimized, shadow-mode, and realized. **observed process data where available; synthetic design-space scenarios for optimization evidence; no production causal claim** A human authority remains required before any operational action; autonomous execution is disabled.

## Implementation and acceptance

- Implementation: `src/trustdoe/signature_algorithm.py`
- Windows acceptance test: `tests/test_signature_algorithm.py`
- Required acceptance result: `4 tests, OK`, with invalid inputs and no-feasible cases controlled explicitly.

## Release boundary

This signature is release-ready only when this contract, the research-validation protocol, the machine-readable governance artifact, the existing Airlines 1.5x gates, and the final integrity/hash checks all pass together.
