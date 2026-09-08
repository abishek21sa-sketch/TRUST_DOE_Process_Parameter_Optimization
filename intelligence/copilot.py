"""TRUST process-science copilot: deterministic evidence guidance with optional Gemini."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"

def status() -> dict[str, Any]:
    return {"provider": "Google Gemini", "model": DEFAULT_MODEL, "key_present": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")), "deterministic_fallback": True, "temperature": 0, "claim_boundary": "TRUST recommendations remain shadow/qualification evidence until plant validation and engineer approval."}

def _deterministic(message: str, context: dict[str, Any]) -> str:
    q = message.casefold()
    if any(k in q for k in ("doe", "experiment", "next", "information")):
        next_step = "Open DOE Design Studio or Experiment Budget, inspect information value and safety margin, then approve the next run explicitly."
    elif any(k in q for k in ("safe", "safety", "trust region", "qualification")):
        next_step = "Review the conservative safety lower bound, safe-grid share, and qualification state before considering a recipe recommendation."
    elif any(k in q for k in ("model", "gp", "gaussian", "quadratic", "surface")):
        next_step = "Compare the Gaussian-process champion against the quadratic challenger using leave-one-out error and inspect the published NIST provenance."
    else:
        next_step = "Start at Campaign Control, trace the evidence to the current response surface and safety gate, and keep release authority with the engineer."
    return ("Deterministic TRUST process-science readout\n\n" f"Question: {message.strip()}\n\n" f"Recommended path: {next_step}\n" f"Evidence: {context.get('evidence', 'NIST reference data, GP/challenger comparison, SAFE-TRUST, and qualification gates')}\n" "Boundary: this is not a plant release, process authorization, or causal claim.")

def _gemini(message: str, context: dict[str, Any]) -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
    body = {"system_instruction": {"parts": [{"text": "You are a process-development and DOE copilot. Deterministic model metrics, safety bounds, provenance, and qualification gates are authoritative. Never authorize a production recipe or invent plant validation."}]}, "contents": [{"role": "user", "parts": [{"text": f"Context: {json.dumps(context, sort_keys=True)}\nQuestion: {message.strip()}"}]}], "generationConfig": {"temperature": 0, "seed": 42, "maxOutputTokens": 700}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_MODEL}:generateContent", data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    with urllib.request.urlopen(req, timeout=25) as response: data = json.loads(response.read().decode())
    text = "\n".join(p.get("text", "") for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", []) if p.get("text"))
    if not text.strip(): raise RuntimeError("Gemini returned no visible text")
    return text.strip()

def build_response(message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}; fallback = _deterministic(message, context)
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return {**status(), "answer": fallback, "provider": "deterministic", "model": "rule-based", "fallback": True}
    try: return {"answer": _gemini(message, context), "provider": "Google Gemini", "model": DEFAULT_MODEL, "fallback": False, **status()}
    except (OSError, urllib.error.URLError, json.JSONDecodeError, RuntimeError) as exc:
        return {**status(), "answer": fallback, "provider": "deterministic-fallback", "model": "rule-based", "fallback": True, "error": type(exc).__name__}
