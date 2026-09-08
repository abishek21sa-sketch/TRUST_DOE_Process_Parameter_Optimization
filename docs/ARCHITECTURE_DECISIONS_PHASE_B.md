# Phase B Architecture Decisions

| Component | Technology | Why it fits this project | Why not the common portfolio default |
|---|---|---|---|
| Sequential learning | scikit-learn Gaussian Processes | Small-data, uncertainty-aware process experimentation | Unlike predictive-maintenance style supervised prediction, posterior uncertainty directly controls the next experiment |
| Acquisition optimization | SciPy differential evolution | Continuous nonconvex recipe search over normalized process coordinates | Avoids forcing a MILP onto a continuous experimental-design problem |
| Experimental information | Quadratic RSM information matrix / D-optimal log-det gain | Ties Bayesian search back to DOE information geometry | This is process experimentation, not scheduling/resource allocation |
| Calibration | K-fold conformal absolute residuals | Adds an empirical uncertainty radius without claiming perfect Bayesian calibration | Makes safety gating auditable rather than relying on GP standard deviation alone |
| Robustness | NumPy/SciPy Monte Carlo | Perturbs the released recipe under process drift | Used for recipe qualification rather than a factory digital-twin simulation |
| Phase B product shell | dependency-free HTML Canvas/SVG workbench | Clean-extract, offline, zero-build acceptance while the interaction model is proven | Avoids prematurely freezing another React/sidebar dashboard; final product can migrate this proven interaction to SvelteKit |
| Persistence | JSON evidence artifacts for Phase B | Reproducible benchmark/replay evidence | PostgreSQL is deferred until the enterprise campaign service is introduced |

The architectural identity is an **experimental-learning workstation**, not a mission-control dashboard.
