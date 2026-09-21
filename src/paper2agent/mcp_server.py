from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .security import safe_resource_path


def create_server(workspace: Path, name: str = "paper2agent-resource") -> Any:
    try:
        from fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("MCP support requires: pip install 'paper2agent-skill[mcp]'") from exc

    mcp = FastMCP(name)

    def text_resource(relative_path: str) -> str:
        path = safe_resource_path(workspace, relative_path)
        if not path.is_file():
            return json.dumps({"status": "unavailable", "path": relative_path})
        return path.read_text(encoding="utf-8", errors="replace")

    @mcp.resource("paper://manuscript")
    def manuscript() -> str:
        return text_resource("extracted/manuscript.md")

    @mcp.resource("paper://source-map")
    def source_map() -> str:
        return text_resource("extracted/source_map.json")

    @mcp.resource("paper://resource-manifest")
    def resource_manifest() -> str:
        return text_resource("resources/resource_manifest.json")

    @mcp.resource("paper://provenance")
    def provenance() -> str:
        return text_resource("reports/provenance.json")

    @mcp.resource("paper://limitations")
    def limitations() -> str:
        return text_resource("reports/limitations.md")

    @mcp.prompt()
    def paper_qa(question: str) -> str:
        return ("Answer only from the exposed paper resources. Cite the relevant source location. "
                "If the resources do not support an answer, say that it is unavailable and do not invent it.\n\n"
                f"Question: {question}")

    return mcp


def write_server_launcher(workspace: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    workspace_literal = repr(str(workspace.resolve()))
    output.write_text(
        "from pathlib import Path\n"
        "from paper2agent.mcp_server import create_server\n\n"
        f"mcp = create_server(Path({workspace_literal}))\n"
        "mcp.run()\n",
        encoding="utf-8",
    )
    return output
