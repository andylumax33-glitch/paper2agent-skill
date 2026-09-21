from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse

from .security import sha256_file

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)


def classify_source(value: str) -> str:
    path = Path(value).expanduser()
    if path.is_file():
        return "pdf" if path.suffix.lower() == ".pdf" else "file"
    if DOI_RE.fullmatch(value.strip()):
        return "doi"
    if urlparse(value).scheme in {"http", "https"}:
        return "url"
    raise ValueError("Input must be a local file, HTTP(S) URL, or DOI")


def register_local_source(source: str, workspace: Path) -> dict[str, object]:
    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    target_dir = workspace / "source"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / path.name
    target.write_bytes(path.read_bytes())
    return {
        "source_id": "paper-main",
        "source_type": classify_source(str(path)),
        "path": str(target.relative_to(workspace)),
        "input_sha256": sha256_file(target),
    }


def register_remote_source(source: str, workspace: Path) -> dict[str, object]:
    value = source.strip()
    url = f"https://doi.org/{quote(value, safe='/')}" if DOI_RE.fullmatch(value) else value
    if urlparse(url).scheme not in {"http", "https"}:
        raise ValueError("Remote source must use HTTP(S) or be a DOI")
    target_dir = workspace / "source"
    target_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".pdf" if value.lower().endswith(".pdf") else ".html"
    target = target_dir / f"paper{suffix}"
    request = urllib.request.Request(url, headers={"User-Agent": "paper2agent-skill/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        target.write_bytes(response.read())
    return {
        "source_id": "paper-main",
        "source_type": "pdf" if suffix == ".pdf" else "html",
        "path": str(target.relative_to(workspace)),
        "source_url": url,
        "input_sha256": sha256_file(target),
    }
