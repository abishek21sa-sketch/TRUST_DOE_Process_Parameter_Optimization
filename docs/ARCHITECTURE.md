# Phase A Architecture Decision Record

| Component | Choice | Why it fits this project | Why it is distinct here |
|---|---|---|---|
| Experiment state | Python dataclass campaign ledger | explicit experiment lineage and state transitions | experiment campaign, not asset/factory command center |
| Probabilistic AI | scikit-learn Gaussian Processes | sparse DOE + uncertainty is the native problem | uncertainty drives experiment choice rather than failure/RUL prediction |
| IE core | DOE + response-surface information geometry | physical experiments are scarce and expensive | experiment design is the product's mathematical center |
| OR/control | TRUST-DOE-S constrained sequential acquisition | couples improvement, information and trust region | not a maintenance/scheduling/network MILP |
| Simulation | process-oracle + perturbation robustness | validates candidate recipes without claiming realized benefit | posterior/process-window experiment logic rather than factory DES |
| Data | CSV canonical experiment adapter + SHA-256 evidence | future AM Bench / lab exports map to observations | experiment records, not generic telemetry |
| UI | intentionally deferred to Product phase | avoids building another generic dashboard before the state model is correct | final view will be a trust-region response-surface workbench |
