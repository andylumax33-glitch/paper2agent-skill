from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mcp_server import write_server_launcher
from .models import to_jsonable
from .paper_parser import parse_local_paper
from .provenance import write_provenance
from .reports import write_report
from .resource_discovery import discover_resources
from .resource_manifest import build_manifest
from .source_registry import classify_source, register_local_source, register_remote_source
from .tool_candidates import scan_python_candidates


def ingest(source: str, workspace: Path) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    source_kind = classify_source(source)
    registration = register_local_source(source, workspace) if source_kind in {"pdf", "file"} else register_remote_source(source, workspace)
    source_path = workspace / str(registration["path"])
    source_map, text = parse_local_paper(source_path, workspace)
    (workspace / "extracted" / "source_map.json").write_text(
        json.dumps(to_jsonable(source_map), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    write_report(workspace, "step0-source-registration.json", {"status": "verified", "registration": registration})
    write_report(workspace, "step1-paper-parser.json", {"status": "verified", "source_map": to_jsonable(source_map)})
    write_provenance(workspace, tuple())
    (workspace / "reports" / "limitations.md").write_text(
        "# Limitations\n\n- External code has not been executed.\n- Discovered links require verification before use.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "success", "workspace": str(workspace), "text_chars": len(text)}, ensure_ascii=False))


def discover(workspace: Path) -> None:
    manuscript = workspace / "extracted" / "manuscript.md"
    source_map_path = workspace / "extracted" / "source_map.json"
    if not manuscript.is_file() or not source_map_path.is_file():
        raise FileNotFoundError("Run ingest before discover")
    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    candidates = discover_resources(manuscript.read_text(encoding="utf-8"))
    build_manifest(workspace, source_map, candidates)
    write_report(workspace, "step2-resource-discovery.json", {"status": "source-grounded", "candidates": to_jsonable(candidates)})
    print(json.dumps({"status": "success", "candidates": len(candidates)}, ensure_ascii=False))


def build_mcp(workspace: Path, output: Path) -> None:
    write_server_launcher(workspace, output)
    write_report(workspace, "step3-mcp-build.json", {"status": "verified", "server_path": str(output)})
    print(json.dumps({"status": "success", "server": str(output)}, ensure_ascii=False))


def scan_tools(workspace: Path, repository: Path) -> None:
    candidates = scan_python_candidates(repository, workspace)
    write_report(
        workspace,
        "tool-candidates.json",
        {
            "status": "inferred",
            "candidates": [
                {
                    "path": candidate.path,
                    "function_names": list(candidate.function_names),
                    "execution_allowed": candidate.execution_allowed,
                }
                for candidate in candidates
            ],
        },
    )
    print(json.dumps({"status": "success", "candidates": len(candidates)}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a resource-first paper agent workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("source")
    ingest_parser.add_argument("--workspace", type=Path, required=True)
    discover_parser = subparsers.add_parser("discover")
    discover_parser.add_argument("workspace", type=Path)
    mcp_parser = subparsers.add_parser("build-mcp")
    mcp_parser.add_argument("workspace", type=Path)
    mcp_parser.add_argument("--output", type=Path, required=True)
    tools_parser = subparsers.add_parser("scan-tools")
    tools_parser.add_argument("workspace", type=Path)
    tools_parser.add_argument("repository", type=Path)
    args = parser.parse_args()
    if args.command == "ingest":
        ingest(args.source, args.workspace)
    elif args.command == "discover":
        discover(args.workspace)
    elif args.command == "scan-tools":
        scan_tools(args.workspace, args.repository)
    else:
        build_mcp(args.workspace, args.output)
