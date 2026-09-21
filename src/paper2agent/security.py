from __future__ import annotations

import hashlib
from pathlib import Path


class WorkspaceSecurityError(ValueError):
    """Raised when a path leaves the authorized workspace."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_within_workspace(path: Path, workspace: Path) -> Path:
    workspace_root = workspace.resolve()
    candidate = path.resolve()
    try:
        candidate.relative_to(workspace_root)
    except ValueError as exc:
        raise WorkspaceSecurityError(f"Path is outside workspace: {candidate}") from exc
    return candidate


def safe_resource_path(workspace: Path, relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path:
        raise WorkspaceSecurityError("Invalid resource path")
    return ensure_within_workspace(workspace / relative_path, workspace)
