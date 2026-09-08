# Phase D2 — Interactive Process Engineering Workbench

## Purpose
Phase D2 repairs Phase D's Windows release defects and converts the report-style product shell into an executable process-development workflow.

## New executable workflows
- Create persistent process-development campaigns.
- Generate factorial, CCD, Box–Behnken, and Latin-hypercube experiment plans.
- Propose model-safe TRUST-DOE shadow experiments.
- Replay or record experiment outcomes into campaign state.
- Run user-configured Monte Carlo drift scenarios.
- Persist decision lineage and SHA-256 evidence hashes.
- Query campaigns and engineering evidence over a local REST-style interface.

## Safety invariant
`production_write_allowed = false` remains invariant. The application is a shadow experimentation and qualification system, not a machine-control service.

## Windows defect repairs
SQLite connections are explicitly closed after every transaction. The Windows acceptance script now checks native process exit codes and cannot print PASS after pytest/build/validator failure.
