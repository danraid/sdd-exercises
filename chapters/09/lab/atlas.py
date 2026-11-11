import copy


EXPECTED_IDS = {f"REQ-{number:03d}" for number in range(1, 7)}


class Atlas:
    """Sequential, in-memory teaching model; not a production API."""

    def __init__(self):
        self._records = {}
        self._keys = {}
        self._next_id = 1

    def submit(self, kind, key):
        if kind not in {"permit", "appointment"}:
            raise ValueError("unsupported kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be non-blank")

        if key in self._keys:
            binding = self._keys[key]
            if binding["kind"] != kind:
                raise ValueError("conflicting key")
            request_id = binding["id"]
            return request_id, self._records[request_id]["state"]

        request_id = f"R{self._next_id}"
        self._records[request_id] = {
            "kind": kind,
            "state": "submitted",
        }
        self._keys[key] = {"kind": kind, "id": request_id}
        self._next_id += 1
        return request_id, "submitted"

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer required")
        record = self._records[request_id]
        next_state = {
            "submitted": "under_review",
            "under_review": "decided",
        }.get(record["state"])
        if target != next_state or next_state is None:
            raise ValueError("invalid transition")
        record["state"] = target
        return target

    def snapshot(self):
        """Return a detached view for this teaching model's assertions."""
        return copy.deepcopy({
            "records": self._records,
            "keys": self._keys,
            "next_id": self._next_id,
        })


def validate_spec(spec, available_names):
    """Resolve names and basic structure; do not judge test meaning."""
    if not isinstance(spec, dict) or spec.get("version") != "1.2":
        raise ValueError("expected candidate version 1.2")
    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = []
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("requirement must be an object")
        req_id = requirement.get("id")
        invariant = requirement.get("invariant")
        tests = requirement.get("tests")
        if not isinstance(req_id, str) or not req_id.strip():
            raise ValueError("invalid requirement ID")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("invalid invariant")
        if not isinstance(tests, list) or not tests:
            raise ValueError("tests must be a non-empty list")
        if any(not isinstance(name, str) or name not in available_names
               for name in tests):
            raise ValueError("unresolved test name")
        ids.append(req_id)

    if len(ids) != len(set(ids)) or set(ids) != EXPECTED_IDS:
        raise ValueError("unexpected or duplicate requirement IDs")
