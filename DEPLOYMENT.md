# Trust DOE deployment

The process-development workbench (static `workbench/`) is served by Vercel. The experiment-service API (`scripts/start_platform.py`, a long-running `ThreadingHTTPServer`) is served by Render. These are two separate deployments — Vercel does not run the API.

Note on `[tool.vercel]` in `pyproject.toml`: this only wires up Vercel's Python runtime when the entrypoint resolves to a WSGI/ASGI `app`/`application` object. `scripts/start_platform.py` exposes a raw `http.server.BaseHTTPRequestHandler` subclass (`Handler`) meant to be run via `ThreadingHTTPServer(...).serve_forever()`, not a WSGI/ASGI callable, and there is no `api/` directory for Vercel's file-based Python function convention either. So that declaration does not make Vercel serve `/api/*` — do not rely on it. The API must run on Render (or another always-on Python host).

The frontend bridge at the top of `workbench/index.html` defaults `window.__TRUSTDOE_API_BASE__` to the Render URL (`https://trust-doe-api.onrender.com`) for any non-localhost origin. If that Render service does not exist or is down, the browser raises `TypeError: Failed to fetch` — that is the exact failure mode if the Render Blueprint below has not been created yet.

## Deploy steps

1. **Render (API)** — Create a Render Blueprint from this repository (the checked-in `render.yaml` defines it). Keep the service name `trust-doe-api` so it matches the hostname hardcoded in `workbench/index.html`; Render will run `python scripts/start_platform.py` and health-check `/api/health`.
2. Confirm `https://trust-doe-api.onrender.com/api/health` returns `status: ok`.
3. **Vercel (frontend)** — Import this repository in Vercel with Root Directory at the repository root. The checked-in `vercel.json` publishes `workbench/` as a static site; no build step or serverless functions are required.
4. `TRUSTDOE_CORS_ORIGIN` on Render is already set to `*` in `render.yaml`, so the Vercel-hosted frontend can call the Render API cross-origin without further CORS configuration. Narrow it to the exact Vercel origin once that URL is known, if desired.
5. Optional: add `GEMINI_API_KEY` only as a Render secret (never in frontend code).
6. If you ever point the frontend at a different backend host, set `window.__TRUSTDOE_API_BASE__` in an inline script before the bridge script runs in `workbench/index.html`, and update `TRUSTDOE_CORS_ORIGIN` on that backend to match the Vercel origin.

Open the Vercel URL, create a campaign, generate a design, and ask Trust DOE Copilot which bounded experiment to inspect next.
