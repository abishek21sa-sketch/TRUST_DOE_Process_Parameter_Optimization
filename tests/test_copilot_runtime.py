from intelligence.copilot import build_response, status


def test_copilot_has_keyless_evidence_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    state = status()
    response = build_response("Which safe experiment should run next?")
    assert state["deterministic_fallback"] is True
    assert response["fallback"] is True
    assert response["provider"] == "deterministic"
    assert "Boundary:" in response["answer"]
