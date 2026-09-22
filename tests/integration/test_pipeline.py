from pathlib import Path

from paper2agent.cli import build_mcp, discover, ingest


def test_resource_pipeline(tmp_path: Path) -> None:
    paper = tmp_path / "paper.txt"
    paper.write_text("Paper title\nMethods\nCode https://github.com/example/project\n", encoding="utf-8")
    workspace = tmp_path / "workspace"
    ingest(str(paper), workspace)
    discover(workspace)
    output = workspace / "generated/server.py"
    build_mcp(workspace, output)
    assert (workspace / "extracted/manuscript.md").is_file()
    assert (workspace / "resources/resource_manifest.json").is_file()
    assert output.is_file()
