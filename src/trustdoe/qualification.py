from __future__ import annotations

def qualification_gate(*, feasibility_probability:float, safety_p05:float, evidence_class:str, data_ready:bool, model_validated:bool)->dict:
    reasons=[]
    if not data_ready: reasons.append('DATA_NOT_READY')
    if not model_validated: reasons.append('MODEL_VALIDATION_INCOMPLETE')
    if feasibility_probability < .98: reasons.append('ROBUST_FEASIBILITY_BELOW_98_PERCENT')
    if safety_p05 <= 0: reasons.append('LOWER_TAIL_SAFETY_MARGIN_NONPOSITIVE')
    external=evidence_class in {'HISTORICAL_VALIDATION','EXTERNAL_VALIDATION'}
    if reasons:
        state='HOLD_FOR_MORE_EVIDENCE'
    elif external:
        state='EXTERNALLY_VALIDATED_CANDIDATE'
    else:
        state='QUALIFIED_SHADOW_RECIPE'
    return {'state':state,'reasons':reasons,'production_write_allowed':False,
            'external_validation_complete':external,
            'governance_note':'Machine write remains blocked; release requires plant governance outside this software.'}
