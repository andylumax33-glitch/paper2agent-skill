from pathlib import Path

import pytest

from paper2agent.security import WorkspaceSecurityError, ensure_within_workspace, safe_resource_path, sha256_file


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    assert sha256_file(path) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_path_traversal_is_blocked(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceSecurityError):
        safe_resource_path(tmp_path, "../outside.txt")


def test_workspace_path_is_allowed(tmp_path: Path) -> None:
    path = safe_resource_path(tmp_path, "extracted/paper.md")
    assert path == (tmp_path / "extracted/paper.md").resolve()
