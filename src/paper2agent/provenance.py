from __future__ import annotations

from pathlib import Path

from .models import Evidence, to_jsonable
from .reports import write_report


def write_provenance(workspace: Path, evidence: tuple[Evidence, ...]) -> Path:
    return write_report(workspace, "provenance.json", {"status": "source-grounded", "evidence": to_jsonable(evidence)})
