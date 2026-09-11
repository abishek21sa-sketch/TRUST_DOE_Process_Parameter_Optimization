"""Temporary CI diagnostic: emit GitHub Actions ::notice:: workflow commands so mismatch
details show up as visible Annotations on the run page -- unlike step logs or the Job
Summary, Annotations render for anyone without needing repo log-viewer sign-in. Delete once
verify_release_integrity.py's real failure is root-caused and fixed."""
from __future__ import annotations
import hashlib, json, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def notice(msg: str) -> None:
    # ::notice:: messages are capped well under 4KB and GitHub only surfaces the first ~10
    # annotations prominently, so keep each one short and only emit a handful.
    msg = msg.replace("\n", " ").replace("%", "%25").replace("\r", "%0D")[:900]
    print(f"::notice::{msg}")


notice(f"env: python={sys.version.split()[0]} platform={platform.platform()}")

manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
inv = json.loads((ROOT / "SOURCE_SHA256SUMS.json").read_text(encoding="utf-8"))

mismatches = []
for item in manifest.get("evidence_inventory", []):
    p = ROOT / item["path"]
    if p.is_file():
        raw = p.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != item["sha256"]:
            mismatches.append(("evidence", item["path"], item["sha256"], actual, raw))
    else:
        mismatches.append(("evidence-missing", item["path"], item["sha256"], None, None))

for rel, expected in inv.get("files", {}).items():
    p = ROOT / rel
    if p.is_file():
        raw = p.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != expected:
            mismatches.append(("source", rel, expected, actual, raw))
    else:
        mismatches.append(("source-missing", rel, expected, None, None))

notice(f"total mismatches: {len(mismatches)}")

for kind, path, expected, actual, raw in mismatches[:8]:
    if raw is None:
        notice(f"{kind} path={path!r} (file not found)")
        continue
    tail = raw[-30:]
    has_crlf = b"\r\n" in raw
    notice(
        f"{kind} path={path!r} bytes={len(raw)} expected={expected[:16]} actual={actual[:16]} "
        f"has_crlf={has_crlf} tail={tail!r}"
    )
