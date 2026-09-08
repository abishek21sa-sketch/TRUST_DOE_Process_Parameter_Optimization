# Architecture Decisions — Phase D

| Component | Technology | Why it fits | Portfolio differentiation |
|---|---|---|---|
| Numerical core | Python / NumPy / SciPy / scikit-learn | Preserves validated Phase A–C math | Reuse is evidence-driven, not template-driven |
| Campaign ledger | SQLite / `sqlite3` | Local, transactional, zero-service Windows acceptance | Distinct from network/database-centric manufacturing apps |
| Product server | Python `ThreadingHTTPServer` | Small REST/read API surface without framework dependency | Avoids default FastAPI pattern |
| UI | Custom HTML/CSS/Canvas JS | Scientific workstation, experimental design/model/qualification workspaces | No dark command center, no left KPI dashboard metaphor |
| OR | SciPy HiGHS + robust nonlinear search | Existing validated formulation remains primary | Solver selected by formulation, not resume variety |
| Public data boundary | governed adapter manifest + schema readiness | Prevents fabricated fields | Explicit external-validation boundary |
