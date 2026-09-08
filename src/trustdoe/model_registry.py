"""File-backed, hashable model evidence registry.

The registry is deliberately append-only at the model-id level: the evidence hash is
computed from the scientific payload, and the resulting JSON file can be included in
release manifests or qualification reports without trusting an in-memory object.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


@dataclass(frozen=True)
class ModelEvidence:
    model_id: str
    response: str
    dataset: str
    algorithms_tested: list[str]
    metrics: dict
    selected_model: str
    reason: str
    timestamp: str
    evidence_hash: str


class ModelRegistry:
    def __init__(self, root: str | Path = "models/registry"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def register(
        self,
        *,
        response: str,
        dataset: str,
        algorithms_tested: list[str],
        metrics: dict,
        selected_model: str,
        reason: str,
    ) -> ModelEvidence:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "response": response,
            "dataset": dataset,
            "algorithms_tested": list(algorithms_tested),
            "metrics": metrics,
            "selected_model": selected_model,
            "reason": reason,
            "timestamp": timestamp,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        item = ModelEvidence(
            model_id="MODEL-" + digest[:12],
            evidence_hash=digest,
            **payload,
        )
        target = self.root / f"{item.model_id}.json"
        target.write_text(json.dumps(asdict(item), indent=2, sort_keys=True), encoding="utf-8")
        return item
