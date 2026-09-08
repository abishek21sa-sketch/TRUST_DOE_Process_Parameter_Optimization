from pathlib import Path
import json, sqlite3
root=Path(__file__).resolve().parents[1]
p=json.loads((root/'artifacts'/'phaseD_report.json').read_text())
checks={
 'nine_workspaces':len(p['workspaces'])==9,
 'shadow_gate':p['production_write_allowed'] is False and p['governance']['machine_write']=='BLOCKED',
 'design_catalog':len(p['design_studio'])>=4,
 'multiple_models':len(p['model_laboratory']['objective'])>=3,
 'scenario_matrix':len(p['scenario_laboratory'])>=4,
 'scenario_probabilities':all(0<=x['feasibility_probability']<=1 for x in p['scenario_laboratory']),
 'qualification_governed':p['qualification_gate']['production_write_allowed'] is False,
 'public_data_honest':p['public_data_sources'][0]['validation']=='EXTERNAL_DATASET_EXECUTION_PENDING',
 'campaign_persistent':(root/'runtime'/'trustdoe.db').exists(),
}
with sqlite3.connect(root/'runtime'/'trustdoe.db') as con:
    checks['ledger_has_observations']=con.execute('select count(*) from observations').fetchone()[0]>0
print(json.dumps({'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks},indent=2))
if not all(checks.values()): raise SystemExit(1)
print('PHASE D VALIDATOR: PASS')
