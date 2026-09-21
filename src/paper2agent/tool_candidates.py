from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .security import ensure_within_workspace


@dataclass(frozen=True)
class ToolCandidate:
    path: str
    function_names: tuple[str, ...]
    status: str = "inferred"
    execution_allowed: bool = False


def scan_python_candidates(repository: Path, workspace: Path) -> tuple[ToolCandidate, ...]:
    workspace = workspace.resolve()
    repository_root = ensure_within_workspace(repository, workspace)
    candidates: list[ToolCandidate] = []
    for path in sorted(repository_root.rglob("*.py")):
        if any(part.startswith(".") for part in path.relative_to(repository_root).parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        functions = tuple(line.split("def ", 1)[1].split("(", 1)[0].strip() for line in text.splitlines() if line.lstrip().startswith("def "))
        if functions:
            candidates.append(ToolCandidate(str(path.relative_to(workspace)), functions))
    return tuple(candidates)


def execute_python_candidate(
    script: str,
    workspace: Path,
    *,
    authorized: bool = False,
    timeout_seconds: int = 60,
) -> dict[str, object]:
    if not authorized:
        return {"status": "blocked", "reason": "Explicit execution authorization is required."}
    target = ensure_within_workspace(workspace / script, workspace)
    if target.suffix != ".py" or not target.is_file():
        return {"status": "blocked", "reason": "Only an existing Python file inside the workspace may run."}
    try:
        result = subprocess.run(
            [sys.executable, str(target)],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "failed", "reason": "Candidate exceeded the execution timeout."}
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }
