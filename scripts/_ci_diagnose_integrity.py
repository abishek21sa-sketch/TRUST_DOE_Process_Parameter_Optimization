"""Temporary CI diagnostic: dump exact mismatch details to $GITHUB_STEP_SUMMARY so they're
readable from the Actions run page without needing repo log-viewer access. Delete once
verify_release_integrity.py's real failure is root-caused and fixed."""
from __future__ import annotations
import hashlib, json, os, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
lines = []


def emit(s: str = "") -> None:
    lines.append(s)


emit(f"### Release integrity diagnostic")
emit(f"- Python: `{sys.version}`")
emit(f"- Platform: `{platform.platform()}`")
emit(f"- CWD: `{Path.cwd()}`")
emit("")

manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
inv = json.loads((ROOT / "SOURCE_SHA256SUMS.json").read_text(encoding="utf-8"))

mismatches = []
for item in manifest.get("evidence_inventory", []):
    p = ROOT / item["path"]
    if not p.is_file():
        mismatches.append(("evidence-missing", item["path"], item["sha256"], None, None, None))
        continue
    raw = p.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != item["sha256"]:
        mismatches.append(("evidence", item["path"], item["sha256"], actual, len(raw), raw[:80]))

for rel, expected in inv.get("files", {}).items():
    p = ROOT / rel
    if not p.is_file():
        mismatches.append(("source-missing", rel, expected, None, None, None))
        continue
    raw = p.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        mismatches.append(("source", rel, expected, actual, len(raw), raw[:80]))

emit(f"**Total mismatches: {len(mismatches)}**")
emit("")
emit("| kind | path | expected | actual | bytes | first 80 bytes (repr) |")
emit("|---|---|---|---|---|---|")
for kind, path, expected, actual, nbytes, head in mismatches[:40]:
    head_repr = repr(head)[:120] if head is not None else ""
    emit(f"| {kind} | `{path}` | `{str(expected)[:12]}` | `{str(actual)[:12]}` | {nbytes} | `{head_repr}` |")
if len(mismatches) > 40:
    emit(f"\n... and {len(mismatches) - 40} more")

output = "\n".join(lines)
print(output)
if summary_path:
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(output + "\n")
