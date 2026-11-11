from copy import deepcopy

BASE_VERSION = "teaching-base-1"
EXTENDED_VERSION = "teaching-extension-2"
BASE_IDS = [f"LAB-{number:03d}" for number in range(1, 6)]


class BaseAtlas:
    """Sequential teaching API with a deliberately shallow replay."""

    def __init__(self):
        self._records = {}
        self._next_id = 1

    def submit(self, key, payload):
        if key in self._records:
            record = self._records[key]
            if record["payload"] != payload:
                raise ValueError("conflicting payload")
            # Deliberate defect: the identifier survives, review does not.
            record["reviewed"] = False
            return record["id"]

        application_id = f"A-{self._next_id}"
        self._next_id += 1
        self._records[key] = {
            "id": application_id,
            "payload": payload,
            "reviewed": False,
        }
        return application_id

    def mark_reviewed(self, key):
        self._records[key]["reviewed"] = True

    def snapshot(self, key):
        return deepcopy(self._records[key])


class Atlas(BaseAtlas):
    """Extension: matching replay leaves the existing record intact."""

    def submit(self, key, payload):
        if key in self._records:
            record = self._records[key]
            if record["payload"] != payload:
                raise ValueError("conflicting payload")
            return record["id"]
        return super().submit(key, payload)


def validate_spec(base, spec, test_class):
    """Validate this fixture's structure, not test semantics."""
    if base.get("version") != BASE_VERSION:
        raise ValueError("unexpected base version")
    if spec.get("version") != EXTENDED_VERSION:
        raise ValueError("unexpected extension version")

    base_reqs = base.get("requirements")
    reqs = spec.get("requirements")
    if not isinstance(base_reqs, list) or not isinstance(reqs, list):
        raise ValueError("requirements must be lists")
    if [r.get("id") for r in base_reqs] != BASE_IDS:
        raise ValueError("unexpected base identifiers")
    if len(reqs) != len(base_reqs) + 1 or reqs[:-1] != base_reqs:
        raise ValueError("base requirements were not preserved")
    if reqs[-1].get("id") != "REQ-006":
        raise ValueError("missing extension requirement")

    seen_ids = set()
    seen_tests = set()
    for requirement in reqs:
        req_id = requirement.get("id")
        invariant = requirement.get("invariant")
        links = requirement.get("tests")
        if not isinstance(req_id, str) or req_id in seen_ids:
            raise ValueError("invalid or duplicate ID")
        seen_ids.add(req_id)
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if not isinstance(links, list) or not links:
            raise ValueError("missing test links")
        for name in links:
            if not isinstance(name, str) or not name.startswith("test_"):
                raise ValueError("invalid test name")
            if name in seen_tests:
                raise ValueError("duplicate test link")
            if not callable(vars(test_class).get(name)):
                raise ValueError("unresolved test")
            seen_tests.add(name)
