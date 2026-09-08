# Phase D — Process Development Platform

Phase D converts the locked Phase A–C computational kernel into a persistent scientific engineering product. It does **not** change the safety boundary: all default evidence is synthetic validation and machine write remains blocked.

## Product workspaces
1. Experiment Design Studio
2. Model Laboratory
3. Autonomous Experiment Studio
4. Operating Window Explorer
5. Recipe Forge
6. Qualification Gate
7. Scenario Laboratory
8. Campaign Ledger
9. Data Gateway

## Architectural choice
The validated Python numerical core remains intact. The product server intentionally uses Python's standard-library threaded HTTP server for this phase rather than introducing another FastAPI/React-style stack. Persistent campaign lineage uses SQLite through the standard library. The browser product is custom HTML/CSS/Canvas JavaScript and is organized as a scientific workstation, not a generic KPI dashboard.

The persistence contract is deliberately separable from analytics so a final production adapter can target PostgreSQL without rewriting DOE, AI, or OR engines.
