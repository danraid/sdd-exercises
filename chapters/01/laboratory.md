# Chapter 01 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

The following is an executable adaptation of the supplied synthetic Atlas core. Save it as `examples/atlas_ch01/atlas.py`. It uses only the Python standard library. The class acts as both the service and its boundary validator: invalid kinds, keys, roles and transitions are rejected with `ContractError`.

```python
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
```

Save the following as `examples/atlas_ch01/test_atlas.py`. Each test creates a fresh service instance, so its outcome does not depend on the order of the other tests.

```python
import unittest

from atlas import AtlasService, ContractError


class AtlasAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.service = AtlasService()

    def test_req001_accepts_only_declared_request_kinds(self):
        permit = self.service.submit("permit", "key-1")
        appointment = self.service.submit("appointment", "key-2")
        self.assertEqual(permit.kind, "permit")
        self.assertEqual(appointment.kind, "appointment")
        with self.assertRaises(ContractError):
            self.service.submit("licence", "key-3")

    def test_req002_replays_idempotently(self):
        first = self.service.submit("permit", "  key-1  ")
        replay = self.service.submit("permit", "key-1")
        self.assertEqual(first.request_id, replay.request_id)
        with self.assertRaises(ContractError):
            self.service.submit("permit", "   ")

    def test_req002_rejects_conflicting_replay(self):
        first = self.service.submit("permit", "key-1")
        with self.assertRaises(ContractError):
            self.service.submit("appointment", "key-1")
        self.assertEqual(self.service.get(first.request_id), first)

    def test_req003_enforces_ordered_lifecycle(self):
        first = self.service.submit("permit", "key-1")
        self.assertEqual(first.status, "submitted")
        review = self.service.advance(first.request_id, "reviewer")
        self.assertEqual(review.status, "under_review")
        decided = self.service.advance(first.request_id, "reviewer")
        self.assertEqual(decided.status, "decided")
        with self.assertRaises(ContractError):
            self.service.advance(first.request_id, "reviewer")
        self.assertEqual(self.service.get(first.request_id), decided)

    def test_req004_blocks_unauthorised_advancement(self):
        first = self.service.submit("appointment", "key-1")
        with self.assertRaises(ContractError):
            self.service.advance(first.request_id, "applicant")
        self.assertEqual(self.service.get(first.request_id), first)


if __name__ == "__main__":
    unittest.main()
```

From the repository root, run:

```text
python -m unittest discover -s examples/atlas_ch01 -v
```

Record the Python version, repository revision, command and actual output alongside the specification version. The intended acceptance outcome is that all five named tests pass; no execution is claimed here. If a test fails, inspect both the implementation and the test against the contract before deciding which artefact needs correction.

To demonstrate why the idempotency test matters, temporarily replace the existing-key branch with code that allocates a fresh request instead. Run the relevant test and record its observed result before restoring the implementation. This is a deliberately introduced fault, not a substitute for a systematic fault analysis. Do not use this teaching service as a public API without defining and implementing the omitted controls.
