from __future__ import annotations
import json, sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
from .domain import Observation

SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS campaigns(
 id TEXT PRIMARY KEY, name TEXT NOT NULL, evidence_class TEXT NOT NULL,
 status TEXT NOT NULL, created_at TEXT NOT NULL, metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations(
 id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id TEXT NOT NULL,
 iteration INTEGER NOT NULL, recipe_json TEXT NOT NULL, objective REAL NOT NULL,
 safety_margin REAL NOT NULL, source TEXT NOT NULL, created_at TEXT NOT NULL,
 FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS decisions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id TEXT NOT NULL,
 kind TEXT NOT NULL, payload_json TEXT NOT NULL, evidence_hash TEXT NOT NULL,
 created_at TEXT NOT NULL, FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);
'''

class CampaignRepository:
    def __init__(self,path:str|Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connection() as con: con.executescript(SCHEMA)

    @contextmanager
    def connection(self):
        con=sqlite3.connect(self.path, timeout=10.0)
        con.row_factory=sqlite3.Row
        try:
            con.execute('PRAGMA foreign_keys=ON')
            yield con
            con.commit()
        except Exception:
            con.rollback(); raise
        finally:
            con.close()

    def upsert_campaign(self,campaign_id:str,name:str,evidence_class='SYNTHETIC_VALIDATION',status='ACTIVE',metadata=None):
        now=datetime.now(timezone.utc).isoformat(); md=json.dumps(metadata or {},sort_keys=True)
        with self.connection() as con:
            existing=con.execute('SELECT created_at FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            created=existing['created_at'] if existing else now
            con.execute('INSERT OR REPLACE INTO campaigns(id,name,evidence_class,status,created_at,metadata_json) VALUES(?,?,?,?,?,?)',
                        (campaign_id,name,evidence_class,status,created,md))

    def clear_campaign_children(self,campaign_id:str):
        with self.connection() as con:
            con.execute('DELETE FROM observations WHERE campaign_id=?',(campaign_id,))
            con.execute('DELETE FROM decisions WHERE campaign_id=?',(campaign_id,))

    def append_observation(self,campaign_id:str,iteration:int,obs:Observation):
        now=datetime.now(timezone.utc).isoformat()
        with self.connection() as con:
            con.execute('INSERT INTO observations(campaign_id,iteration,recipe_json,objective,safety_margin,source,created_at) VALUES(?,?,?,?,?,?,?)',
                        (campaign_id,iteration,json.dumps(list(obs.recipe)),obs.objective,obs.safety_margin,obs.source,now))

    def record_decision(self,campaign_id:str,kind:str,payload:dict)->str:
        raw=json.dumps(payload,sort_keys=True,separators=(',',':')); h=hashlib.sha256(raw.encode()).hexdigest(); now=datetime.now(timezone.utc).isoformat()
        with self.connection() as con:
            con.execute('INSERT INTO decisions(campaign_id,kind,payload_json,evidence_hash,created_at) VALUES(?,?,?,?,?)',(campaign_id,kind,raw,h,now))
        return h

    def list_campaigns(self):
        with self.connection() as con:
            rows=con.execute('SELECT * FROM campaigns ORDER BY created_at DESC').fetchall()
        return [dict(r) for r in rows]

    def campaign_detail(self,campaign_id:str):
        with self.connection() as con:
            c=con.execute('SELECT * FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            if not c: return None
            obs=con.execute('SELECT * FROM observations WHERE campaign_id=? ORDER BY iteration',(campaign_id,)).fetchall()
            dec=con.execute('SELECT * FROM decisions WHERE campaign_id=? ORDER BY id',(campaign_id,)).fetchall()
        return {'campaign':dict(c),'observations':[dict(x) for x in obs],'decisions':[dict(x) for x in dec]}
