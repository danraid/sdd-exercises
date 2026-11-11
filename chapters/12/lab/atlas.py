EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 7)}


def validate_spec(spec, available_tests):
    if spec.get("version") != "1.2-proposed":
        raise ValueError("unexpected specification version")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    seen = set()
    for req in requirements:
        if not isinstance(req, dict):
            raise ValueError("invalid requirement")
        req_id = req.get("id")
        invariant = req.get("invariant")
        tests = req.get("tests")

        if not isinstance(req_id, str) or req_id in seen:
            raise ValueError("missing or duplicate ID")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if (not isinstance(tests, list) or not tests
                or any(not isinstance(t, str) for t in tests)):
            raise ValueError("missing test links")
        if any(t not in available_tests for t in tests):
            raise ValueError("unresolved test link")
        seen.add(req_id)

    if seen != EXPECTED_IDS:
        raise ValueError("unexpected requirement IDs")


class Atlas:
    def __init__(self):
        self._keys = {}
        self._records = {}
        self._next_id = 1

    def submit(self, kind, key):
        if kind not in ("permit", "appointment"):
            raise ValueError("invalid kind")
        if (not isinstance(key, str) or not key.strip()
                or not key.isascii() or len(key) > 32):
            raise ValueError("invalid key")

        if key in self._keys:
            request_id = self._keys[key]
            record = self._records[request_id]
            if record["kind"] != kind:
                raise ValueError("conflicting replay")
            return request_id, record["state"]

        request_id = f"R{self._next_id}"
        self._next_id += 1
        self._keys[key] = request_id
        self._records[request_id] = {
            "kind": kind, "state": "submitted"
        }
        return request_id, "submitted"

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer required")
        record = self._records[request_id]
        next_state = {
            "submitted": "under_review",
            "under_review": "decided"
        }.get(record["state"])
        if next_state is None or target != next_state:
            raise ValueError("invalid transition")
        record["state"] = target
        return target
