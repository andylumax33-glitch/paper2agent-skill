from paper2agent.resource_discovery import discover_resources


def test_discovery_classifies_code_and_data() -> None:
    text = "Code is available at https://github.com/example/project and data at https://zenodo.org/records/1."
    candidates = discover_resources(text)
    assert len(candidates) == 2
    assert candidates[0].resource_type == "code_repository"
    assert candidates[1].resource_type == "dataset_or_model"
