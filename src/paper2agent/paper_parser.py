from __future__ import annotations

import re
from pathlib import Path

from .models import SourceMap
from .security import sha256_file

FIGURE_RE = re.compile(r"(?im)^\s*(?:Fig(?:ure)?\.?\s*\d+[^\n]*|Table\s+\d+[^\n]*)$")
URL_RE = re.compile(r"https?://[^\s)<>\]]+")
KNOWN_HEADINGS = {
    "abstract", "main", "methods", "results", "discussion", "conclusions",
    "data availability", "code availability", "references", "reporting summary",
}


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF support requires: pip install 'paper2agent-skill[pdf]'") from exc
    pages = [(page.extract_text() or "") for page in PdfReader(str(path)).pages]
    return "\n\n".join(pages).strip()


def _extract_text(path: Path) -> str:
    return _extract_pdf(path) if path.suffix.lower() == ".pdf" else path.read_text(encoding="utf-8", errors="replace")


def _title_and_authors(text: str, fallback: str) -> tuple[str, tuple[str, ...]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    try:
        article_index = next(index for index, line in enumerate(lines[:30]) if line.lower() == "article")
    except StopIteration:
        return (lines[0] if lines else fallback), ()
    title_lines: list[str] = []
    author_line = ""
    for line in lines[article_index + 1: article_index + 10]:
        if line.lower().startswith(("here we ", "abstract")):
            break
        if re.search(r"\d", line) and ("," in line or "&" in line or " et al" in line.lower()):
            author_line = line
            break
        if line.lower() not in {"nature", "open access"}:
            title_lines.append(line)
    title = " ".join(title_lines).strip() or fallback
    authors = tuple(
        part.strip(" ✉ ")
        for part in re.split(r",|&", author_line)
        if part.strip() and not part.strip().isdigit()
    ) if author_line else ()
    return title[:300], authors


def parse_local_paper(source_path: Path, workspace: Path) -> tuple[SourceMap, str]:
    text = _extract_text(source_path)
    if not text.strip():
        raise ValueError("The paper produced no extractable text")
    extracted = workspace / "extracted"
    extracted.mkdir(parents=True, exist_ok=True)
    (extracted / "manuscript.md").write_text(text + "\n", encoding="utf-8")
    sections = tuple(
        {"title": line.strip().title(), "text_anchor": line.strip()}
        for line in text.splitlines()
        if line.strip().lower() in KNOWN_HEADINGS
    )
    figures = tuple({"label": match.group(0).strip()} for match in FIGURE_RE.finditer(text))
    doi_match = re.search(r"\bdoi:\s*(10\.\S+)|\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", text, re.I)
    title, authors = _title_and_authors(text, source_path.stem)
    source_map = SourceMap(
        source_id="paper-main",
        source_type="pdf" if source_path.suffix.lower() == ".pdf" else "text",
        title=title[:300],
        authors=authors,
        doi=(doi_match.group(1) or doi_match.group(2)) if doi_match else None,
        input_sha256=sha256_file(source_path),
        sections=sections,
        figures=figures,
    )
    return source_map, text


def extract_urls(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(URL_RE.findall(text)))
