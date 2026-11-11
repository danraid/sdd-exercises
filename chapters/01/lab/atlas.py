"""Synthetic, in-memory Atlas API core; specification v1.0."""
from dataclasses import dataclass
from typing import Dict, Tuple


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Request:
    request_id: str
    kind: str
    status: str = "submitted"


class AtlasService:
    KINDS = frozenset({"permit", "appointment"})
    TRANSITIONS = {
        "submitted": "under_review",
        "under_review": "decided",
    }

    def __init__(self) -> None:
        self._requests: Dict[str, Request] = {}
        self._keys: Dict[str, Tuple[str, str]] = {}

    def submit(self, kind: str, idempotency_key: str) -> Request:
        if kind not in self.KINDS:
            raise ContractError("REQ-001: unsupported request kind")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ContractError("REQ-002: an idempotency key is required")

        key = idempotency_key.strip()
        if key in self._keys:
            previous_kind, request_id = self._keys[key]
            if previous_kind != kind:
                raise ContractError("REQ-002: conflicting key reuse")
            return self._requests[request_id]

        request_id = f"ATL-{len(self._requests) + 1:04d}"
        record = Request(request_id=request_id, kind=kind)
        self._requests[request_id] = record
        self._keys[key] = (kind, request_id)
        return record

    def advance(self, request_id: str, actor_role: str) -> Request:
        if actor_role != "reviewer":
            raise ContractError("REQ-004: only reviewers may advance")
        record = self._requests.get(request_id)
        if record is None:
            raise ContractError("REQ-003: unknown request")
        next_status = self.TRANSITIONS.get(record.status)
        if next_status is None:
            raise ContractError("REQ-003: terminal status")

        revised = Request(record.request_id, record.kind, next_status)
        self._requests[request_id] = revised
        return revised

    def get(self, request_id: str) -> Request:
        try:
            return self._requests[request_id]
        except KeyError as exc:
            raise ContractError("REQ-003: unknown request") from exc
