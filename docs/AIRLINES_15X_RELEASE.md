# TRUST-DOE — Process Parameter Optimization — Airlines-1.5× Depth Candidate

Release: `TRUST_DOE_FORTUNE50_AIRLINES15X_RC4`

## What changed

This release adds a provenance-aware empirical backbone, a live empirical API, project-native historical/entity diagnostics, a named empirical case study, external-source refresh/promotion workflow, live empirical charts, and a 26+ workspace contract in which each workspace has a distinct method/evidence/action definition.

## Current evidence mode

- Source: **CVD tungsten deposition response-surface experiment**
- Source URL: https://www.itl.nist.gov/div898/handbook/pri/section4/pri473.htm
- Mode: **published_external_snapshot**
- Promotion state: **EXTERNAL_EVIDENCE_ACTIVE**
- Local analyzable evidence: **11 rows / 7 fields**
- Workspaces: **26**

## Domain diagnostic

**published NIST CVD quadratic response-surface reconstruction**

Reference metrics:
```json
{
  "runs": 11,
  "center_pred_uniformity_pct": 5.8661,
  "center_pred_stress": 7.79,
  "grid_candidates": 1681
}
```

Decision signal: Use the reconstructed surface to propose the next safe shadow experiment, then let SAFE-TRUST and qualification constraints govern release.

## Analytical chain

source provenance → schema/data-quality checks → entity/factor drilldown → cohort/history comparison → diagnostic ranking → predictive model → original algorithm → OR/simulation escalation → counterfactual challenge → human decision

## Windows gates

Core/offline acceptance:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows_airlines15x_acceptance.ps1
```

External-data promotion (internet required):
```powershell
.\scripts\windows_external_data_promotion.ps1
```

## Claim boundary

External-source results are claimed only when data_mode is refreshed_external or published_external_snapshot; offline_reference remains reference evidence.

The label “Airlines-1.5×” is an internal portfolio-depth target relative to the latest observable Airlines evidence, not an external company certification and not a claim that reference/synthetic data is real production evidence.
