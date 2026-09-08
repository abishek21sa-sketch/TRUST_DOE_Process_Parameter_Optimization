# TRUST-DOE — Process Parameter Optimization — Final Portfolio Build

This repository is the project-native release. Benchmark/RC branding is intentionally kept out of the downloadable project name.

## New decision-campaign layer

The product now includes **Sequential Experiment Campaign**, a multi-scenario workflow that replays the predictive + original-algorithm decision across seven reference realizations and computes the project-specific campaign measure **safe-recipe dispersion + information frontier**.

The campaign is available at `GET /api/project/campaign` and in the workstation. It never grants autonomous operational authority. Final authority remains with the **Process Development Engineer**.

## Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_acceptance.ps1
.\scripts\start_workstation.ps1
```

The first script verifies integrity, predictive/original-algorithm evidence, empirical depth, the new campaign layer and focused tests.
