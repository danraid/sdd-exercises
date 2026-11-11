import json
from pathlib import Path


class Atlas:
    """Synthetic, single-process request store."""

    def __init__(self):
        self._requests = {}

    def submit(self, key, payload):
        if key in self._requests:
            record = self._requests[key]
            if record["payload"] != payload:
                raise ValueError("idempotency-key conflict")
            return dict(record)

        record = {"key": key, "payload": payload, "status": "active"}
        self._requests[key] = record
        return dict(record)

    def withdraw(self, key):
        self._requests[key]["status"] = "withdrawn"
        return dict(self._requests[key])

    def read(self, key):
        return dict(self._requests[key])


def validate_spec(path, test_class):
    """Resolve this overlay's required fields and test method names."""
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    if spec.get("version") != "atlas-overlay-1.2":
        raise ValueError("unexpected overlay version")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list) or len(requirements) != 1:
        raise ValueError("expected exactly one overlay requirement")

    req = requirements[0]
    if not isinstance(req, dict) or req.get("id") != "REQ-006":
        raise ValueError("expected REQ-006")

    invariant = req.get("invariant")
    if not isinstance(invariant, str) or not invariant.strip():
        raise ValueError("invariant must be non-empty")

    links = req.get("tests")
    if not isinstance(links, list) or not links:
        raise ValueError("tests must be a non-empty list")
    for name in links:
        if (
            not isinstance(name, str)
            or not name.startswith("test_req006_")
            or not callable(getattr(test_class, name, None))
        ):
            raise ValueError(f"unresolved test: {name!r}")
    return True
