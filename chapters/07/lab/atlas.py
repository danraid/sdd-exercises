from copy import deepcopy


class Atlas:
    """Synthetic, in-memory teaching model."""

    def __init__(self):
        self.records = {}

    def submit(self, key, kind):
        if key in self.records:
            record = self.records[key]
            if record["kind"] != kind:
                raise ValueError("conflicting kind")
            return deepcopy(record)

        if kind != "maintenance":
            raise ValueError("unsupported kind")

        record = {"key": key, "kind": kind, "status": "submitted"}
        self.records[key] = record
        return deepcopy(record)

    def review(self, key, reviewer):
        if not reviewer:
            raise PermissionError("reviewer flag required")
        record = self.records[key]
        if record["status"] != "submitted":
            raise ValueError("invalid transition")
        record["status"] = "reviewed"
        return deepcopy(record)


def with_description(submit):
    """Return a boundary around an existing submission callable.

    The description is a boundary argument. Remaining arguments are passed
    unchanged to submit; the description is not stored by this wrapper.
    """
    def guarded(description, *args, **kwargs):
        if not isinstance(description, str) or not description.strip():
            raise ValueError("description must be a non-blank string")
        return submit(*args, **kwargs)

    return guarded


def validate_spec(document, version, expected_ids, test_class):
    """Check structure and named methods, not test meaning or execution."""
    if document.get("version") != version:
        raise ValueError("unexpected version")
    requirements = document.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = [item.get("id") for item in requirements]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        raise ValueError("unexpected or duplicate requirement IDs")

    for item in requirements:
        for field in ("name", "invariant"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("missing " + field)
        links = item.get("tests")
        if not isinstance(links, list) or not links:
            raise ValueError("missing test links")
        if len(links) != len(set(links)):
            raise ValueError("duplicate test links")
        for link in links:
            if not isinstance(link, str) or not link.startswith("test_"):
                raise ValueError("invalid test link")
            if not callable(getattr(test_class, link, None)):
                raise ValueError("unresolved test link: " + link)


def validate_migration(baseline, proposed):
    """Check the chapter's explicitly permitted v1.0-to-v1.1 changes."""
    old = {item["id"]: item for item in baseline["requirements"]}
    new = {item["id"]: item for item in proposed["requirements"]}

    for req_id in ("REQ-001", "REQ-003", "REQ-004"):
        if old[req_id] != new[req_id]:
            raise ValueError("baseline requirement changed: " + req_id)

    before = old["REQ-002"]
    after = new["REQ-002"]
    if before["name"] != "Idempotent submission":
        raise ValueError("unexpected baseline name")
    if after["name"] != "Replay consistency":
        raise ValueError("unexpected migrated name")
    if before["invariant"] != after["invariant"]:
        raise ValueError("REQ-002 invariant changed")
    if before["tests"] != ["test_req002_replay", "test_req002_conflict"]:
        raise ValueError("unexpected baseline links")
    if after["tests"] != [
        "test_req002_replay_preserves_record",
        "test_req002_conflict_rejected",
    ]:
        raise ValueError("unexpected migrated links")
