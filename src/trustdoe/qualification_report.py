"""Deterministic qualification report export; prose remains evidence-bound."""
from dataclasses import asdict, dataclass
from pathlib import Path
import html, json

@dataclass(frozen=True)
class QualificationReport:
    campaign: str; dataset: str; recommended_recipe: dict; expected_performance: dict
    risk: list[str]; uncertainty: dict; experiments: list[dict]; models: list[dict]
    simulation: dict; qualification: dict; evidence: list[str]
    def export(self, directory):
        root=Path(directory); root.mkdir(parents=True,exist_ok=True); data=asdict(self)
        (root/'process_qualification_report.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        body=''.join(f'<h2>{html.escape(k.replace("_"," ").title())}</h2><pre>{html.escape(json.dumps(v,indent=2))}</pre>' for k,v in data.items())
        (root/'process_qualification_report.html').write_text('<!doctype html><meta charset="utf-8"><title>Process Qualification Report</title>'+body,encoding='utf-8')
        return root
