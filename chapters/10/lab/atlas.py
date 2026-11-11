import copy


EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 7)}
VERSION = "1.2-ch10-proposal"


def validate_spec(spec, available_tests):
    """Structural checks only; no semantic or policy judgement."""
    if not isinstance(spec, dict) or spec.get("version") != VERSION:
        raise ValueError("unexpected specification version")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    seen = set()
    for item in requirements:
        if not isinstance(item, dict):
            raise ValueError("invalid requirement")
        req_id = item.get("id")
        invariant = item.get("invariant")
        links = item.get("tests")
        if not isinstance(req_id, str) or req_id in seen:
            raise ValueError("invalid or duplicate requirement ID")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if not isinstance(links, list) or not links:
            raise ValueError("missing test links")
        if any(not isinstance(name, str) or name not in available_tests
               for name in links):
            raise ValueError("unresolved test link")
        seen.add(req_id)

    if seen != EXPECTED_IDS:
        raise ValueError("unexpected requirement IDs")


class Atlas:
    """Single-process teaching model; roles are not authenticated."""

    def __init__(self):
        self._keys = {}
        self._records = {}
        self._next_id = 1

    def snapshot(self):
        return copy.deepcopy((self._keys, self._records, self._next_id))

    def submit(self, kind, key):
        if kind not in ("permit", "appointment"):
            raise ValueError("invalid kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("blank key")

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
            "kind": kind,
            "state": "submitted",
        }
        return request_id, "submitted"

    def advance(self, request_id, target, role):
        record = self._records[request_id]
        if role != "reviewer":
            raise PermissionError("reviewer required")
        next_state = {
            "submitted": "under_review",
            "under_review": "decided",
        }.get(record["state"])
        if next_state is None or target != next_state:
            raise ValueError("illegal transition")
        record["state"] = target
        return target
