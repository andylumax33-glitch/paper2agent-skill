from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import Evidence, ResourceCandidate
from .paper_parser import extract_urls

CODE_HOSTS = {"github.com", "gitlab.com", "bitbucket.org"}
DATA_HOSTS = {"zenodo.org", "figshare.com", "osf.io", "dataverse.org", "dryad.org", "huggingface.co"}
CODE_TERMS = re.compile(r"(?:code|source|github|gitlab|repository|implementation)", re.I)
DATA_TERMS = re.compile(r"(?:data|dataset|supplement|zenodo|figshare|osf|dryad|database)", re.I)


def _classify(url: str, context: str) -> tuple[str, str, float]:
    host = (urlparse(url).hostname or "").lower()
    if host in CODE_HOSTS:
        return "code_repository", "official_or_related_code", 0.85
    if host in DATA_HOSTS:
        return "dataset_or_model", "associated_data_or_model", 0.78
    if CODE_TERMS.search(context):
        return "project_page", "possible_code_or_project_page", 0.55
    if DATA_TERMS.search(context):
        return "supplementary_or_data_page", "possible_supplementary_material", 0.55
    return "external_link", "unclassified", 0.30


def discover_resources(text: str, source_id: str = "paper-main") -> tuple[ResourceCandidate, ...]:
    candidates = []
    for url in extract_urls(text):
        clean_url = url.rstrip(".,;:)")
        resource_type, relation, confidence = _classify(clean_url, text[max(0, text.find(url) - 300): text.find(url) + 300])
        candidates.append(ResourceCandidate(
            url=clean_url,
            resource_type=resource_type,
            relation=relation,
            confidence=confidence,
            evidence=(Evidence(source_id, clean_url, "URL discovered in paper text"),),
            status="inferred",
        ))
    return tuple(candidates)
