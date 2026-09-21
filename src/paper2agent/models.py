from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Status = Literal["verified", "source-grounded", "inferred", "missing", "conflicting", "unavailable"]


@dataclass(frozen=True)
class Evidence:
    source_id: str
    locator: str
    description: str = ""
    status: Status = "source-grounded"


@dataclass(frozen=True)
class ResourceCandidate:
    url: str
    resource_type: str
    relation: str
    confidence: float
    evidence: tuple[Evidence, ...] = ()
    status: Status = "inferred"


@dataclass(frozen=True)
class SourceMap:
    source_id: str
    source_type: str
    title: str
    authors: tuple[str, ...]
    doi: str | None
    input_sha256: str | None
    sections: tuple[dict[str, Any], ...] = ()
    figures: tuple[dict[str, Any], ...] = ()
    tables: tuple[dict[str, Any], ...] = ()
    equations: tuple[dict[str, Any], ...] = ()


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value
