from __future__ import annotations
import math
import numpy as np

class GaussianProcess:
    def __init__(self,length=.28,noise=1e-6): self.length,self.noise=length,noise
    def _k(self,A,B):
        A=np.atleast_2d(A); B=np.atleast_2d(B); d=((A[:,None,:]-B[None,:,:])**2).sum(2); return np.exp(-.5*d/(self.length**2))
    def fit(self,X,y):
        self.X=np.asarray(X,float); self.y=np.asarray(y,float); K=self._k(self.X,self.X)+np.eye(len(self.X))*self.noise; self.L=np.linalg.cholesky(K); self.alpha=np.linalg.solve(self.L.T,np.linalg.solve(self.L,self.y)); return self
    def predict(self,X):
        X=np.atleast_2d(X); Ks=self._k(X,self.X); mean=Ks@self.alpha; v=np.linalg.solve(self.L,Ks.T); var=np.maximum(1-(v*v).sum(0),1e-12); return mean,np.sqrt(var)

class SafeTrust:
    """SAFE-TRUST: selects the next experiment from a trust region using conservative safety and information."""
    def choose(self,cands,obj_mean,obj_sd,safe_mean,safe_sd,current_best):
        out=[]
        for i,x in enumerate(cands):
            lcb=float(safe_mean[i]-1.645*safe_sd[i]); ei=max(0.0,current_best-float(obj_mean[i])); info=float(obj_sd[i]); radius=float(np.linalg.norm(x))
            score=ei+.55*info-.08*radius
            out.append({'index':i,'x':np.asarray(x).tolist(),'safety_lcb':lcb,'score':score,'expected_improvement':ei,'information':info,'feasible':lcb>=0})
        feasible=[x for x in out if x['feasible']]; return max(feasible,key=lambda z:z['score']) if feasible else max(out,key=lambda z:z['safety_lcb'])

def _truth(x):
    a,b=x; objective=(a-.62)**2+1.4*(b-.38)**2+.08*math.sin(8*a*b); safety=.48-1.35*(a-.58)**2-1.1*(b-.42)**2
    return objective,safety

def _run_decision_core(seed=7):
    r=np.random.default_rng(seed); X=r.uniform(.12,.88,(18,2)); yo=[]; ys=[]
    for x in X:
        o,s=_truth(x); yo.append(o+r.normal(0,.012)); ys.append(s+r.normal(0,.02))
    gp_o=GaussianProcess(.25).fit(X,yo); gp_s=GaussianProcess(.30).fit(X,ys); H=r.uniform(.15,.85,(24,2)); htruth=np.array([_truth(x) for x in H]); ho,_=gp_o.predict(H); hs,_=gp_s.predict(H); rmse_o=float(np.sqrt(np.mean((ho-htruth[:,0])**2))); rmse_s=float(np.sqrt(np.mean((hs-htruth[:,1])**2)))
    grid=np.array([[a,b] for a in np.linspace(.25,.8,12) for b in np.linspace(.2,.75,12)]); mo,so=gp_o.predict(grid); ms,ss=gp_s.predict(grid)
    choice=SafeTrust().choose(grid,mo,so,ms,ss,min(yo)); naive=int(np.argmax(np.maximum(0,min(yo)-mo)))
    return {'project':'TRUST-DOE','ml_family':'Gaussian-process surrogate learning','prediction_target':'process response and safety-margin posterior','model_validation':{'metric':'holdout RMSE','objective_rmse':rmse_o,'safety_rmse':rmse_s,'split':'independent synthetic points'},'prediction':{'objective_mean':float(mo[choice['index']]),'objective_sd':float(so[choice['index']]),'safety_mean':float(ms[choice['index']]),'safety_sd':float(ss[choice['index']])},'original_algorithm':'SAFE-TRUST-v1','decision':choice,'counterfactual':{'naive_policy':'maximum expected improvement without safety confidence','index':naive,'safety_lcb':float(ms[naive]-1.645*ss[naive]),'disagrees':naive!=choice['index']},'uncertainty':'Posterior standard deviations reported for objective and safety surrogate.','or_escalation':'Use selected experiment to update D-optimal DOE / trust-region robust recipe qualification.','tool_trace':['fit objective GP','fit safety GP','generate trust-region candidates','SAFE-TRUST confidence gate','challenge max-EI','qualify through DOE workflow'],'limitations':['reference synthetic process truth','kernel hyperparameters fixed in bundled validation'],'abstention_conditions':['no conservative safe candidate','calibration drift','extrapolation outside experimental envelope'],'user_aid':['inspect posterior surfaces','run recommended shadow experiment','record observation','re-qualify recipe'],'human_authority':'PROCESS_DEVELOPMENT_ENGINEER','autonomous_execution':False}


def run_decision(seed=None):
    from empirical.backbone import run_empirical_reference
    import inspect
    sig=inspect.signature(_run_decision_core)
    if seed is None:
        out=_run_decision_core()
    else:
        out=_run_decision_core(seed)
    emp=run_empirical_reference()
    out["empirical_backbone"]=emp
    from empirical.public_data_backbone import integrate_decision
    out=integrate_decision(out)
    out.setdefault("tool_trace",[]).insert(0,"resolve empirical data provenance and source mode")
    out.setdefault("user_aid",[]).append("open empirical case study and entity/history drilldowns before approval")
    return out
