# Frontend Demo Flow — TRUST-DOE — Process Parameter Optimization

This product keeps its own visual language: **process-development laboratory notebook / response surface**. The shared contract is behavioral evidence, not a shared layout or theme.

## Native entrypoint

`workbench/index.html`

## Project-specific demo sequence

1. construct DOE
2. fit response and safety models
3. explore operating window
4. select trust-region experiment
5. process engineer qualifies or holds

## Evidence requirements

The screen must show the project-native inputs, objective, constraints, baseline/counterfactual, evidence class, signature decision, and human approval/hold state. The product must not imply autonomous actuation.

## API evidence surface

The read-only signature evidence endpoint is `/api/governance/signature`. Its response is linked to `artifacts/fortune50_capability_benchmark.json` and exposes the current decision, baseline, sensitivity/counterfactual evidence, and human-gated status.
