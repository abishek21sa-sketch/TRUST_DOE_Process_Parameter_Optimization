# Phase B Validation Evidence

Evidence class: **SYNTHETIC_VALIDATION**

Source-build validation performed before packaging:

- 20 automated tests passed.
- Phase B evidence pipeline completed.
- Phase B release validator passed all nine release-contract checks.
- Python source/script compilation passed.
- Safe Experiment Cockpit HTTP smoke test returned both `index.html` and `data.json` successfully.
- Experiment Race includes TRUST-DOE-S, Random-LHS, Static DOE and unconstrained Bayesian optimization.
- Release frontier contains Pareto-efficient and policy-qualified shadow candidates.
- Autonomous machine write remains disabled in every release object.

Representative deterministic Phase B benchmark, seed 2026, six adaptive experiments after the common initial campaign:

| Strategy | Best safe objective | Unsafe trials |
|---|---:|---:|
| TRUST-DOE-S | 0.08509 | 0 |
| Random-LHS | 0.38945 | 0 |
| Static DOE | 0.38945 | 4 |
| Unconstrained BO | 0.11375 | 0 |

Lower objective is better. This benchmark is not external manufacturing evidence and does not establish universal superiority.

The exact distributed ZIP is additionally clean-extracted and regression-tested before delivery; that packaging check is reported with the release message because it occurs after this file is frozen into the artifact.
