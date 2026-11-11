"""Synthetic, single-process Atlas teaching model."""

EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 6)}
KINDS = {"permit", "appointment"}
NEXT = {"submitted": "under_review", "under_review": "decided"}


def validate_spec(spec, available_tests):
    """Check specification structure and named test links."""
    if not isinstance(spec, dict) or spec.get("version") != "1.1":
        raise ValueError("expected specification version 1.1")
    if not isinstance(spec.get("scope"), str) or not spec["scope"].strip():
        raise ValueError("missing scope")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = set()
    for req in requirements:
        if not isinstance(req, dict):
            raise ValueError("requirement must be an object")
        rid = req.get("id")
        if not isinstance(rid, str) or rid in ids:
            raise ValueError("missing or duplicate requirement ID")
        ids.add(rid)

        invariant = req.get("invariant")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError(f"{rid}: missing invariant")
        tests = req.get("tests")
        if not isinstance(tests, list) or not tests:
            raise ValueError(f"{rid}: missing test links")
        for name in tests:
            if not isinstance(name, str) or name not in available_tests:
                raise ValueError(f"{rid}: unresolved test link")

    if ids != EXPECTED_IDS:
        raise ValueError("unexpected requirement IDs")


class Atlas:
    def __init__(self):
        self._by_key = {}
        self._by_id = {}
        self._next_id = 1

    def submit(self, kind, key):
        if kind not in KINDS:
            raise ValueError("invalid kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be non-blank")

        if key in self._by_key:
            record = self._by_key[key]
            if record["kind"] != kind:
                raise ValueError("conflicting key reuse")
            return record["id"], record["state"]

        request_id = f"R{self._next_id}"
        self._next_id += 1
        record = {"id": request_id, "kind": kind, "state": "submitted"}
        self._by_key[key] = record
        self._by_id[request_id] = record
        return request_id, record["state"]

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer role required")
        record = self._by_id[request_id]  # Unknown IDs raise KeyError.
        if NEXT.get(record["state"]) != target or target is None:
            raise ValueError("invalid transition")
        record["state"] = target
        return target
