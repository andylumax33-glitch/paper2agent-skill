from pathlib import Path

from paper2agent.tool_candidates import execute_python_candidate, scan_python_candidates


def test_scan_python_candidates(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    repository = workspace / "repo"
    repository.mkdir(parents=True)
    (repository / "example.py").write_text("def run(data):\n    return data\n", encoding="utf-8")
    candidates = scan_python_candidates(repository, workspace)
    assert candidates[0].function_names == ("run",)
    assert candidates[0].execution_allowed is False


def test_execution_requires_authorization(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    script = workspace / "candidate.py"
    workspace.mkdir()
    script.write_text("print('should not run')\n", encoding="utf-8")
    result = execute_python_candidate("candidate.py", workspace)
    assert result["status"] == "blocked"
