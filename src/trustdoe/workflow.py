from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json, uuid
import numpy as np
from .persistence import CampaignRepository
from .domain import CampaignState, Observation
from .process import SyntheticAMOracle
from .doe import latin_hypercube
from .design_studio import full_factorial, central_composite, box_behnken, design_metrics
from .controller import select_next_experiment
from .scenario_lab import scenario_matrix
from .release import build_release_frontier, release_summary
from .governance import build_release_certificate, verify_release_certificate

DESIGN_BUILDERS={
    'FULL_FACTORIAL_2': lambda s,n,seed: full_factorial(s,2),
    'CENTRAL_COMPOSITE': lambda s,n,seed: central_composite(s,center_reps=max(2,n or 6)),
    'BOX_BEHNKEN': lambda s,n,seed: box_behnken(s,center_reps=max(1,n or 5)),
    'LATIN_HYPERCUBE': lambda s,n,seed: latin_hypercube(s,max(6,n or 24),seed=seed),
}

class WorkflowService:
    def __init__(self, db_path: str|Path):
        self.repo=CampaignRepository(db_path)
        self.oracle=SyntheticAMOracle(seed=2026)

    def create_campaign(self, name:str, evidence_class='SYNTHETIC_VALIDATION', initial_design='LATIN_HYPERCUBE', runs=14, seed=2026)->dict:
        cid='CMP-'+uuid.uuid4().hex[:8].upper()
        self.repo.upsert_campaign(cid,name,evidence_class=evidence_class,metadata={'initial_design':initial_design,'seed':seed})
        design=self.generate_design(initial_design,runs,seed)['rows']
        for i,row in enumerate(design,1):
            obs=self.oracle.evaluate(np.asarray(row,dtype=float))
            self.repo.append_observation(cid,i,obs)
        self.repo.record_decision(cid,'CAMPAIGN_CREATED',{'design':initial_design,'runs':len(design),'seed':seed})
        return self.repo.campaign_detail(cid)

    def generate_design(self, family:str, runs:int=24, seed:int=2026)->dict:
        family=family.upper()
        if family not in DESIGN_BUILDERS: raise ValueError('Unsupported design family')
        d=np.asarray(DESIGN_BUILDERS[family](self.oracle.space,runs,seed),dtype=float)
        metrics=design_metrics(self.oracle.space,d)
        return {'family':family,'rows':d.tolist(),'metrics':metrics,'factors':[{'name':f.name,'low':f.low,'high':f.high,'unit':f.unit} for f in self.oracle.space.factors]}

    def _state(self,campaign_id:str)->CampaignState:
        detail=self.repo.campaign_detail(campaign_id)
        if not detail: raise KeyError(campaign_id)
        state=CampaignState(trust_radius=0.55)
        md=json.loads(detail['campaign']['metadata_json'] or '{}')
        state.trust_radius=float(md.get('trust_radius',0.55))
        for row in detail['observations']:
            state.append(Observation(tuple(json.loads(row['recipe_json'])),float(row['objective']),float(row['safety_margin']),row['source']))
        return state

    def propose_shadow_trial(self,campaign_id:str, seed:int=2026)->dict:
        state=self._state(campaign_id)
        pool=latin_hypercube(self.oracle.space,2200,seed=seed+state.iteration)
        decision=select_next_experiment(state,self.oracle.space,pool,beta=1.28)
        payload={
          'campaign_id':campaign_id,'iteration':state.iteration+1,'recipe':list(decision.recipe),
          'predicted_objective':decision.predicted_objective,'predicted_objective_std':decision.objective_std,
          'predicted_safety_margin':decision.predicted_safety,'predicted_safety_std':decision.safety_std,
          'acquisition_score':decision.score,'information_gain':decision.information_gain,
          'production_write_allowed':False,'decision_mode':'SHADOW_EXPERIMENT_ONLY'
        }
        payload['evidence_hash']=self.repo.record_decision(campaign_id,'SHADOW_TRIAL_PROPOSAL',payload)
        return payload

    def record_observation(self,campaign_id:str, recipe:list[float], objective:float|None=None, safety_margin:float|None=None, source='MANUAL_SHADOW_OBSERVATION')->dict:
        state=self._state(campaign_id)
        x=np.asarray(recipe,dtype=float)
        if not self.oracle.space.contains(x): raise ValueError('Recipe outside governed process bounds')
        if objective is None or safety_margin is None:
            simulated=self.oracle.evaluate(x)
            objective=simulated.objective if objective is None else objective
            safety_margin=simulated.safety_margin if safety_margin is None else safety_margin
            source='SYNTHETIC_REPLAY' if source=='MANUAL_SHADOW_OBSERVATION' else source
        obs=Observation(tuple(map(float,x)),float(objective),float(safety_margin),source)
        self.repo.append_observation(campaign_id,state.iteration+1,obs)
        self.repo.record_decision(campaign_id,'OBSERVATION_RECORDED',{'iteration':state.iteration+1,'source':source,'safe':obs.safe})
        return {'iteration':state.iteration+1,'safe':obs.safe,'objective':obs.objective,'safety_margin':obs.safety_margin,'source':obs.source}

    def custom_scenarios(self,campaign_id:str, sigma_fractions:list[float])->dict:
        state=self._state(campaign_id); inc=state.incumbent()
        # reuse oracle evaluation with deterministic MC tailored to requested drift levels
        rng=np.random.default_rng(2026); span=self.oracle.space.highs-self.oracle.space.lows
        rows=[]
        for sigma in sigma_fractions:
            xs=np.clip(np.asarray(inc.recipe)+rng.normal(0,sigma*span,size=(1800,self.oracle.space.dimension)),self.oracle.space.lows,self.oracle.space.highs)
            vals=[self.oracle.evaluate(x) for x in xs]
            obj=np.array([v.objective for v in vals]); safe=np.array([v.safety_margin for v in vals])
            rows.append({'sigma_fraction':float(sigma),'objective_mean':float(obj.mean()),'objective_p95':float(np.quantile(obj,.95)),'safety_p05':float(np.quantile(safe,.05)),'feasibility_probability':float(np.mean(safe>=0))})
        self.repo.record_decision(campaign_id,'CUSTOM_SCENARIO_RUN',{'sigma_fractions':sigma_fractions,'results':rows})
        return {'campaign_id':campaign_id,'incumbent':list(inc.recipe),'scenarios':rows}
    def release_assurance(self,campaign_id:str, seed:int=2026, n_candidates:int=36, stress_samples:int=180)->dict:
        state=self._state(campaign_id)
        detail=self.repo.campaign_detail(campaign_id)
        if not detail: raise KeyError(campaign_id)
        frontier=build_release_frontier(state,self.oracle.space,self.oracle,n_candidates=max(12,min(int(n_candidates),96)),stress_samples=max(80,min(int(stress_samples),800)),seed=seed)
        summary=release_summary(frontier)
        decisions=detail.get('decisions',[])
        latest=decisions[-1]['evidence_hash'] if decisions else None
        cert=build_release_certificate(
            campaign_id=campaign_id, release_summary=summary, evidence_class=detail['campaign']['evidence_class'],
            observation_count=len(detail.get('observations',[])), latest_decision_hash=latest,
        )
        cert['verification']=verify_release_certificate(cert)
        cert['evidence_hash']=self.repo.record_decision(campaign_id,'RELEASE_ASSURANCE_CERTIFICATE',cert)
        return cert

