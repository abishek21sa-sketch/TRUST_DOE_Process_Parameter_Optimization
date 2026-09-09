# Trust DOE deployment

The experiment-service API runs on Render and the process-development workbench runs on Vercel. The copilot uses a deterministic safety fallback when Gemini is not configured.

1. Create a Render Blueprint from this repository. Keep the service name `trust-doe-api`; Render starts `scripts/start_platform.py` and checks `/api/health`.
2. Confirm `https://trust-doe-api.onrender.com/api/health` returns `status: ok`.
3. Import the same repository in Vercel and leave Root Directory at the repository root. The checked-in `vercel.json` publishes `workbench/`.
4. Open the Vercel URL, create a campaign, generate a design, and ask Trust DOE Copilot which bounded experiment to inspect next.
5. Optional: add `GEMINI_API_KEY` only as a Render secret.

The frontend bridge is at the top of `workbench/index.html`; update it if the Render service is renamed.
