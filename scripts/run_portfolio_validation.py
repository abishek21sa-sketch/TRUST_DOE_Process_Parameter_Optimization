from __future__ import annotations
import json
from pathlib import Path
from trustdoe.portfolio_validation import write_portfolio_certificate

root = Path(__file__).resolve().parents[1]
payload = write_portfolio_certificate(root / "artifacts" / "portfolio_validation.json")
print(json.dumps({
    "release": payload["release"],
    "qualification": payload["qualification"],
    "evidence_hash": payload["evidence_hash"],
}, indent=2))
print("TRUST_DOE_PORTFOLIO_VALIDATION=PASS")
