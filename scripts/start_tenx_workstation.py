from __future__ import annotations
import json, sys, webbrowser, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tenx.engine import run_decision
from empirical.backbone import run_empirical_reference
from campaign.engine import run_campaign
from intelligence.engine import lifecycle_report, run_agent
from intelligence.copilot import build_response as build_copilot_response, status as copilot_status
UI=ROOT/'tenx_ui'
class H(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        rel=urlparse(path).path.lstrip('/') or 'index.html'; return str(UI/rel)
    def _json(self,obj,status=200):
        raw=json.dumps(obj,indent=2).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.send_header('X-Autonomous-Execution','BLOCKED'); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        p=urlparse(self.path).path
        if p in ('/','/index.html'):
            raw=(UI/'index.html').read_text(encoding='utf-8').replace('</body>','<script src="/copilot.js"></script></body>').encode()
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        if p=='/api/copilot/status': return self._json(copilot_status())
        if p=='/api/tenx/decision':
            try:return self._json(run_decision())
            except Exception as e:return self._json({'error':type(e).__name__,'detail':str(e)},500)
        if p=='/api/EMPIRICAL/empirical':
            try:return self._json(run_empirical_reference())
            except Exception as e:return self._json({'error':type(e).__name__,'detail':str(e)},500)
        if p=='/api/project/campaign':
            try:return self._json(run_campaign())
            except Exception as e:return self._json({'error':type(e).__name__,'detail':str(e)},500)
        if p=='/api/ml/lifecycle':
            try:return self._json(lifecycle_report())
            except Exception as e:return self._json({'error':type(e).__name__,'detail':str(e)},500)
        if p=='/api/agent/run':
            try:return self._json(run_agent())
            except Exception as e:return self._json({'error':type(e).__name__,'detail':str(e)},500)
        if p=='/api/tenx/health':return self._json({'status':'ok','mode':'DOMAIN_NATIVE_INTELLIGENCE_WORKSTATION','ml_lifecycle':True,'agent_planning':True,'autonomous_execution':False})
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path != '/api/copilot/chat':
            self.send_error(404); return
        try:
            size=int(self.headers.get('Content-Length','0')); payload=json.loads(self.rfile.read(size) or b'{}'); message=str(payload.get('message','')).strip()
            if not message or len(message)>2000: return self._json({'error':'message must be between 1 and 2000 characters'},422)
            return self._json(build_copilot_response(message, {'evidence':'NIST reference data, GP/challenger comparison, SAFE-TRUST, and qualification gates','mode':'engineer-review-only'}))
        except Exception as e:
            return self._json({'error':type(e).__name__,'detail':str(e)},422)
    def log_message(self,fmt,*args): print('[TENX]',fmt%args)
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--port',type=int,default=8899); ap.add_argument('--no-browser',action='store_true'); a=ap.parse_args()
    url=f'http://127.0.0.1:{a.port}'
    if not a.no_browser: threading.Timer(.8,lambda:webbrowser.open(url)).start()
    print('TENX workstation ->',url); ThreadingHTTPServer(('127.0.0.1',a.port),H).serve_forever()
