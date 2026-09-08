from empirical.public_data_backbone import data_backbone_status


def test_public_case_exposes_explicit_model_comparison():
    case = data_backbone_status()["case_study"]
    assert case["status"] == "ACTIVE"
    assert len(case["model_comparison"]) == 2
    assert case["selected_model"] in {row["model"] for row in case["model_comparison"]}
    assert sum(bool(row["selected"]) for row in case["model_comparison"]) == 1
