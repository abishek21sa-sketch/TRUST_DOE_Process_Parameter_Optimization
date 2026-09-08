from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

root = Path(__file__).resolve().parents[1] / "workbench"
os.chdir(root)
print("TRUST-DOE Safe Experiment Cockpit")
print("Open http://127.0.0.1:8765")
ThreadingHTTPServer(("127.0.0.1", 8765), SimpleHTTPRequestHandler).serve_forever()
