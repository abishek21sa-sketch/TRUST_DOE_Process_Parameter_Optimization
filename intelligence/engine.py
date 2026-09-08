from __future__ import annotations
from tenx.engine import run_decision
from campaign.engine import run_campaign
from empirical.backbone import run_empirical_reference

def lifecycle_report():
    d=run_decision(13); v=d['model_validation']; p=d.get('prediction',{})
    rmse=max(float(v.get('objective_rmse',0)),float(v.get('safety_rmse',0)))
    sigma=max(float(p.get('objective_sd',0)),float(p.get('safety_sd',0)))
    state='REFIT_REQUIRED' if rmse>.16 or sigma>.36 else ('WATCH' if rmse>.10 or sigma>.24 else 'QUALIFIED')
    public_data=d.get('public_data_backbone',{})
    return {'public_data_state':public_data.get('dataset_state'),'public_evidence_gate':d.get('public_evidence_gate'),'model_family':d['ml_family'],'target':d['prediction_target'],'validation':v,'posterior_uncertainty':round(sigma,6),'readiness':state,'retrain_trigger':'refit GP and re-estimate kernel if holdout RMSE >0.10 or posterior sigma >0.24 near proposed recipe','monitoring':['posterior coverage','objective RMSE','safety RMSE','kernel conditioning','safe-set contraction'],'registry_state':'GP_SHADOW' if state!='QUALIFIED' else 'GP_QUALIFIED','source_mode':run_empirical_reference().get('data_mode')}

def run_agent():
    d=run_decision(13); life=lifecycle_report(); steps=['reconstruct response surface','fit objective GP','fit safety GP','compute conservative safe set']
    state='EXPERIMENT_REVIEW'
    public_gate=d.get('public_evidence_gate')
    if public_gate=='REFERENCE_MODE_HOLD_FOR_REAL_DATA_CLAIM':
        steps.append('flag external public-data acquisition gap; prohibit real-data performance claim')
        state='REFERENCE_MODE_HOLD'
    if life['readiness']=='REFIT_REQUIRED': steps += ['request additional D-optimal calibration runs','refit surrogate before recipe proposal']; state='MODEL_HOLD'
    else: steps += ['invoke SAFE-TRUST candidate selection','challenge max-EI unsafe candidate','stage shadow experiment','prepare qualification evidence']
    return {'agent':'Process Development Scientist','objective':'learn the process efficiently without crossing qualification risk','prediction':d.get('prediction'),'decision':d['decision'],'decision_state':state,'chosen_tool_sequence':steps,'why_this_sequence':'posterior uncertainty controls whether the agent explores, refits, or advances a safe recipe','challenge':d['counterfactual'],'ml_lifecycle':life,'operator_actions':['inspect response/uncertainty surface','run proposed shadow recipe','record result and update GP','approve qualification only after safe window stabilizes'],'human_authority':d['human_authority'],'autonomous_execution':False}
