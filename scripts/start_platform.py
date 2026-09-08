from __future__ import annotations
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import argparse, json, os, uuid

ROOT=Path(__file__).resolve().parents[1]
SOURCE_ROOT=ROOT/'src'
import sys
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0,str(SOURCE_ROOT))

from trustdoe.persistence import CampaignRepository
from trustdoe.workflow import WorkflowService
from trustdoe.signature_algorithm import select_recipe as signature_select, ablation as signature_ablation, sensitivity as signature_sensitivity

WORKBENCH=ROOT/'workbench'
DEFAULT_DB=Path('/tmp/trustdoe.db') if os.getenv('VERCEL') else ROOT/'runtime'/'trustdoe.db'
DB=Path(os.getenv('TRUSTDOE_DB_PATH',str(DEFAULT_DB)))
SERVICE=WorkflowService(DB)
REPO=CampaignRepository(DB)

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        request_id=getattr(self,'request_id',None) or self.headers.get('X-Request-ID') or f"trust-{uuid.uuid4().hex[:16]}"
        self.request_id=request_id
        self.send_header('X-Request-ID',request_id)
        self.send_header('X-Process-Recipe-Execution','SHADOW_ONLY')
        super().end_headers()
    def translate_path(self,path):
        rel=urlparse(path).path.lstrip('/') or 'index.html'
        return str(WORKBENCH/rel)
    def _json(self,payload,status=200):
        raw=json.dumps(payload).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
    def _body(self):
        n=int(self.headers.get('Content-Length','0') or 0)
        return json.loads(self.rfile.read(n).decode('utf-8')) if n else {}
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/api/health': return self._json({'status':'ok','product':'TRUST-DOE','version':'1.0.0','machine_write':'BLOCKED'})
        if p=='/api/governance/signature':
            candidates=[{'recipe':[0.0,0.0],'objective':0.4,'safety':.95,'information':.05},{'recipe':[2.0,2.0],'objective':.1,'safety':.96,'information':.2}]
            return self._json({'status':'HUMAN_GATED_REFERENCE','signature_algorithm':'TRUST-DOE','decision':signature_select(candidates,[0.0,0.0],1.0,.90),'baseline':signature_ablation(candidates,[0.0,0.0],1.0,.90),'sensitivity':signature_sensitivity(candidates,[0.0,0.0],1.0,.90,.03),'objective':'minimize predicted loss inside a safety-qualified trust region','counterfactual':'trust-region ablation','evidence_artifact':'artifacts/fortune50_capability_benchmark.json','autonomous_execution':False})
        if p=='/api/report': return self._json(json.loads((ROOT/'artifacts'/'phaseD_report.json').read_text()))
        if p=='/api/campaigns': return self._json(REPO.list_campaigns())
        if p.startswith('/api/campaign/'):
            cid=p.rsplit('/',1)[-1]; d=REPO.campaign_detail(cid)
            return self._json(d if d else {'error':'not found'},200 if d else 404)
        return super().do_GET()
    def do_POST(self):
        p=urlparse(self.path).path
        try:
            b=self._body()
            if p=='/api/campaigns':
                return self._json(SERVICE.create_campaign(b.get('name','New process campaign'),b.get('evidence_class','SYNTHETIC_VALIDATION'),b.get('initial_design','LATIN_HYPERCUBE'),int(b.get('runs',14)),int(b.get('seed',2026))),201)
            if p=='/api/design/generate':
                return self._json(SERVICE.generate_design(b.get('family','LATIN_HYPERCUBE'),int(b.get('runs',24)),int(b.get('seed',2026))))
            if p.startswith('/api/campaign/') and p.endswith('/propose'):
                cid=p.split('/')[3]; return self._json(SERVICE.propose_shadow_trial(cid,int(b.get('seed',2026))))
            if p.startswith('/api/campaign/') and p.endswith('/observe'):
                cid=p.split('/')[3]; return self._json(SERVICE.record_observation(cid,b['recipe'],b.get('objective'),b.get('safety_margin'),b.get('source','MANUAL_SHADOW_OBSERVATION')),201)
            if p.startswith('/api/campaign/') and p.endswith('/scenarios'):
                cid=p.split('/')[3]; return self._json(SERVICE.custom_scenarios(cid,[float(x) for x in b.get('sigma_fractions',[.005,.01,.02,.04])]))
            if p.startswith('/api/campaign/') and p.endswith('/release-certificate'):
                cid=p.split('/')[3]; return self._json(SERVICE.release_assurance(cid,int(b.get('seed',2026)),int(b.get('n_candidates',36)),int(b.get('stress_samples',180))))
            return self._json({'error':'not found'},404)
        except KeyError as e:
            return self._json({'error':f'missing or unknown: {e}'},404)
        except (ValueError,RuntimeError,TypeError) as e:
            return self._json({'error':str(e)},400)
        except Exception as e:
            return self._json({'error':f'internal error: {type(e).__name__}: {e}'},500)
    def log_message(self,fmt,*args): print('[TRUST-DOE]',fmt%args)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--port',type=int,default=int(os.getenv('PPO_PORT','8772'))); args=ap.parse_args()
    print(f'TRUST-DOE Process Development Platform v1.0.0 -> http://127.0.0.1:{args.port}')
    print('Machine write: BLOCKED | Default evidence: SYNTHETIC_VALIDATION')
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
