from trustdoe.workflow import WorkflowService


def test_workflow_release_assurance_emits_verified_human_gated_certificate(tmp_path):
    svc=WorkflowService(tmp_path/'campaign.db')
    created=svc.create_campaign('assurance-demo',runs=12,seed=91)
    cid=created['campaign']['id']
    cert=svc.release_assurance(cid,seed=91,n_candidates=16,stress_samples=80)
    assert cert['verification']['valid'] is True
    assert cert['production_write_allowed'] is False
    assert cert['approval_authority']=='PROCESS_DEVELOPMENT_ENGINEER'
    assert cert['decision_state'] in {'ENGINEERING_REVIEW_REQUIRED','HOLD_FOR_MORE_EVIDENCE'}
    detail=svc.repo.campaign_detail(cid)
    assert detail['decisions'][-1]['kind']=='RELEASE_ASSURANCE_CERTIFICATE'
