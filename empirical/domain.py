from pathlib import Path
import csv,math
ROOT=Path(__file__).resolve().parents[1]
def _solve(A,b):
 n=len(A); M=[list(map(float,A[i]))+[float(b[i])] for i in range(n)]
 for c in range(n):
  piv=max(range(c,n),key=lambda r:abs(M[r][c])); M[c],M[piv]=M[piv],M[c]; d=M[c][c] or 1e-12; M[c]=[x/d for x in M[c]]
  for r in range(n):
   if r==c:continue
   f=M[r][c]; M[r]=[M[r][k]-f*M[c][k] for k in range(n+1)]
 return [M[i][-1] for i in range(n)]
def _fit(X,y):
 p=len(X[0]); ata=[[sum(r[i]*r[j] for r in X) for j in range(p)] for i in range(p)]; aty=[sum(r[i]*yy for r,yy in zip(X,y)) for i in range(p)]
 for i in range(p):ata[i][i]+=1e-8
 return _solve(ata,aty)
def domain_diagnostics():
 rows=list(csv.DictReader((ROOT/'data/external/nist_cvd_cci.csv').open())); X=[]; u=[]; s=[]
 for r in rows:
  x=float(r['coded_pressure']); z=float(r['coded_h2_wf6']); X.append([1,x,z,x*z,x*x,z*z]); u.append(float(r['uniformity_pct'])); s.append(float(r['stress']))
 bu,bs=_fit(X,u),_fit(X,s)
 def pred(b,x,z):return sum(c*v for c,v in zip(b,[1,x,z,x*z,x*x,z*z]))
 cand=[]
 for i in range(41):
  x=-1+2*i/40
  for k in range(41):
   z=-1+2*k/40; pu=pred(bu,x,z); ps=pred(bs,x,z); score=(pu/10)+(abs(ps-7.5)/3); cand.append((score,x,z,pu,ps))
 best=min(cand); center=(pred(bu,0,0),pred(bs,0,0))
 return {'analysis':'published NIST CVD quadratic response-surface reconstruction','metrics':{'runs':len(rows),'center_pred_uniformity_pct':round(center[0],4),'center_pred_stress':round(center[1],4),'grid_candidates':len(cand)},'recommended_coded_recipe':{'pressure':round(best[1],3),'h2_wf6':round(best[2],3),'pred_uniformity_pct':round(best[3],4),'pred_stress':round(best[4],4),'reference_score':round(best[0],4)},'coefficients':{'uniformity':[round(x,5) for x in bu],'stress':[round(x,5) for x in bs]},'decision_signal':'Use the reconstructed surface to propose the next safe shadow experiment, then let SAFE-TRUST and qualification constraints govern release.','evidence_boundary':'Published NIST example supports empirical response-surface reconstruction, not production process qualification.'}
