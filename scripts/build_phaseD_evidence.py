from pathlib import Path
from trustdoe.phased import build_phased_evidence
p=build_phased_evidence(Path(__file__).resolve().parents[1])
print('PHASE D EVIDENCE BUILD: PASS')
print('Workspaces:',len(p['workspaces']))
print('Qualification:',p['qualification_gate']['state'])
print('Machine write:',p['governance']['machine_write'])
