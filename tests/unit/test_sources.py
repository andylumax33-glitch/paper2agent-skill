from pathlib import Path

from paper2agent.paper_parser import extract_urls, parse_local_paper
from paper2agent.source_registry import classify_source, register_local_source


def test_classify_sources(tmp_path: Path) -> None:
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"placeholder")
    assert classify_source(str(paper)) == "pdf"
    assert classify_source("10.1038/s41586-026-11044-y") == "doi"
    assert classify_source("https://example.org/paper") == "url"


def test_parse_text_source_and_urls(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("A Paper Title\nMethods\nCode: https://github.com/example/project\n", encoding="utf-8")
    workspace = tmp_path / "workspace"
    registration = register_local_source(str(source), workspace)
    source_map, text = parse_local_paper(workspace / registration["path"], workspace)
    assert source_map.title == "A Paper Title"
    assert "https://github.com/example/project" in extract_urls(text)
    assert (workspace / "extracted/manuscript.md").is_file()
