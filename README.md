## AIRLINES-1.5× DEPTH CANDIDATE

Current release `TRUST_DOE_FORTUNE50_AIRLINES15X_RC4` adds a live empirical/historical analysis layer, 26+ substantive workspaces, project-native domain diagnostics, external-source refresh/provenance, and AI decisions grounded in explicit evidence mode. See `docs/AIRLINES_15X_RELEASE.md`.

# Fortune-50 TENX analytical release

**Internal portfolio target:** Math 10/10 · UI 10/10 · AI 10/10, subject to the evidence boundaries below.

- Repository-authored algorithm: **SAFE-TRUST-v1**
- Unique predictive-learning family: **Gaussian-process surrogate learning**
- Analytical AI role: **AI Experiment Scientist**
- TENX workspaces: **20**
- Operational authority: **human-gated; autonomous execution blocked**

### Test the TENX layer on Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_tenx_acceptance.ps1
.\scripts\start_tenx_workstation.ps1
```

The first command validates prediction → decision → counterfactual → OR escalation → user-aid behavior and a five-seed originality stress suite. The second opens the dedicated analytical workstation.

> **Evidence boundary:** TENX bundled metrics are synthetic/reference validation, not field deployment validation. Existing native Windows, Julia/Go/Rust/frontend, external-data, clinical, or production gates remain applicable where documented.

---

# TRUST-DOE — Autonomous Process Parameter Optimization

**Phase D v0.95.0 — Process Development Platform**

TRUST-DOE is a safe sequential experimentation and robust process-recipe decision system. It is designed around a different operational question from predictive-maintenance, digital-twin, circular-manufacturing, and continuous-improvement applications:

> **Which safe experiment should be run next, what has the process learned, and when is a recipe sufficiently robust to qualify for a governed shadow trial?**

The default benchmark is a synthetic additive-manufacturing process. Synthetic results are never represented as factory validation, and machine write is explicitly blocked.

## Decision workflow

`experiment history → DOE/process science → surrogate/model evidence → TRUST-DOE safe exploration → robust recipe optimization → scenario stress test → qualification gate → persistent evidence ledger`

## Phase D product workspaces

- Experiment Design Studio
- Model Laboratory
- Autonomous Experiment Studio
- Operating Window Explorer
- Recipe Forge
- Qualification Gate
- Scenario Laboratory
- Campaign Ledger
- Data Gateway

## Computational methods

**Artificial Intelligence:** Gaussian-process surrogate modeling with uncertainty, model competition against RSM/tree/boosting baselines, conformal calibration, safe sequential acquisition, active experimentation and drift/readiness signals.

**Industrial Engineering / Process Engineering:** factorial/CCD/Box–Behnken/LHS DOE, information geometry, second-order response surfaces, ANOVA/lack-of-fit, process capability, SPC, sensitivity and robust operating-window reasoning.

**Operations Research:** constrained safe acquisition, robust nonlinear recipe optimization, Pareto operating-window search and finite experimental-budget integer allocation solved with HiGHS. Small budget instances are verified against brute force in tests.

**Simulation:** Monte Carlo parameter-drift stress scenarios and robust feasibility estimates. These are simulated results, not realized benefits.

## Windows acceptance

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_phaseD_acceptance.ps1
```

Then launch the Phase D scientific workstation:

```powershell
.\scripts\start_platform.ps1
```

Default URL: `http://127.0.0.1:8772`

Override the port without editing code:

```powershell
$env:PPO_PORT="8781"
.\scripts\start_platform.ps1
```

## Data boundary

The canonical experiment contract requires the four governed process factors plus `objective` and `safety_margin`. CSV readiness checks reject missing fields. A NIST AM Bench public-data route is documented as **external dataset execution pending**; the repository does not fabricate missing external fields.

## Evidence status

- Phase A: locked
- Phase B: locked
- Phase C: locked
- Phase D: implemented and packaged subject to user Windows acceptance
- Real plant validation: pending
- Production machine write: blocked

See `docs/TECHNICAL_METHODS.md`, `docs/TECHNICAL_METHODS_PHASE_C.md`, `docs/PHASE_D_SCOPE.md`, and the generated `artifacts/phaseD_report.json`.

## Phase D2 — Interactive Process Engineering Workbench (0.96.1)

Phase D2 converts the Phase D report-style shell into an executable campaign workflow. Engineers can create persistent campaigns, generate governed DOE plans, request a TRUST-DOE shadow trial, replay/record an observation, rerun custom drift scenarios, and inspect evidence hashes in the campaign ledger. Machine write remains hard-blocked.

The Windows acceptance gate now fails immediately on any native command failure, and SQLite connections are explicitly closed to prevent Windows file-handle leaks.

## Enterprise operability gate

This source release includes a governed decision-assurance layer, negative-path operability tests, hash-verifiable evidence, and a Windows enterprise acceptance gate. See `docs/ENTERPRISE_OPERABILITY.md`.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\scripts\\windows_enterprise_acceptance.ps1
```


## Public Data Backbone
This release contains a structured public-data layer under `data/raw`, `data/processed`, `data/contracts`, `data/dictionaries`, `data/provenance`, and `data/snapshots`. Run `scripts\fetch_public_data_windows.ps1` when the primary public dataset is not bundled, then run `scripts\windows_real_data_acceptance.ps1`. `artifacts/data_backbone_status.json` records source state, row/feature counts, missingness, SHA-256, validation status, case-study state, claim boundary, model version, and the human decision authority.

The public-data case is `Published NIST CVD Operating-Window Reconstruction` and is wired into `SAFE-TRUST-v1` review. Missing external raw data never silently falls back to a real-data claim; the dossier explicitly enters `REFERENCE_MODE_HOLD_FOR_REAL_DATA_CLAIM`.
