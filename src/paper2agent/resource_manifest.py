from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import ResourceCandidate, SourceMap, to_jsonable
from .reports import write_report


def build_manifest(workspace: Path, source_map: SourceMap | dict[str, Any], candidates: tuple[ResourceCandidate, ...]) -> Path:
    manifest: dict[str, Any] = {
        "manifest_version": "1.0",
        "mode": "resource-only",
        "resources": [
            {"uri": "paper://manuscript", "path": "extracted/manuscript.md", "status": "source-grounded"},
            {"uri": "paper://source-map", "path": "extracted/source_map.json", "status": "verified"},
            {"uri": "paper://resource-manifest", "path": "resources/resource_manifest.json", "status": "verified"},
            {"uri": "paper://limitations", "path": "reports/limitations.md", "status": "source-grounded"},
        ],
        "source": to_jsonable(source_map),
        "candidates": to_jsonable(candidates),
    }
    resources = workspace / "resources"
    resources.mkdir(parents=True, exist_ok=True)
    target = resources / "resource_manifest.json"
    import json
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target
