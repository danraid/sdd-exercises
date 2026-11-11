import copy
import json
import unittest
from pathlib import Path

SPEC_PATH = Path(__file__).with_name("spec.json")
EXPECTED_IDS = {"REQ-002", "REQ-006"}


class Atlas:
    """Synthetic in-memory component; principal is already trusted."""

    def __init__(self):
        self.records = {}
        self.next_receipt = 1

    def create(self, principal, key, payload):
        scope = (principal, key)
        if scope in self.records:
            old_payload, receipt = self.records[scope]
            if old_payload != payload:
                raise ValueError("conflicting replay")
            return receipt

        receipt = f"receipt-{self.next_receipt}"
        self.next_receipt += 1
        self.records[scope] = (payload, receipt)
        return receipt


class BrokenAtlas(Atlas):
    """Deliberate counterexample: mutates state before rejecting."""

    def create(self, principal, key, payload):
        scope = (principal, key)
        if scope in self.records:
            old_payload, receipt = self.records[scope]
            if old_payload != payload:
                self.records[scope] = (payload, receipt)
                raise ValueError("conflicting replay")
        return super().create(principal, key, payload)


def validate_spec(spec, test_class):
    """Resolve local structure and names, not test meaning."""
    if spec.get("version") != "1.2-lab":
        raise ValueError("unexpected specification version")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = []
    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("requirement must be an object")
        identifier = requirement.get("id")
        invariant = requirement.get("invariant")
        tests = requirement.get("tests")
        if not isinstance(identifier, str):
            raise ValueError("missing requirement identifier")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if not isinstance(tests, list) or not tests:
            raise ValueError("missing test links")
        for name in tests:
            if (
                not isinstance(name, str)
                or not name.startswith("test_")
                or not callable(getattr(test_class, name, None))
            ):
                raise ValueError(f"unresolved test: {name!r}")
        ids.append(identifier)

    if len(ids) != len(set(ids)) or set(ids) != EXPECTED_IDS:
        raise ValueError("unexpected or duplicate requirement IDs")


def load_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def check_conflict_invariant(case, service):
    receipt = service.create("resident-a", "k-17", "repair")
    before = copy.deepcopy(service.records)

    with case.assertRaises(ValueError):
        service.create("resident-a", "k-17", "replace")

    case.assertEqual(service.records, before)
    case.assertEqual(
        service.create("resident-a", "k-17", "repair"), receipt
    )


class TestAtlas(unittest.TestCase):
    def test_req002_replays_and_rejects_conflict(self):
        service = Atlas()
        first = service.create("resident-a", "k-17", "repair")
        self.assertEqual(
            service.create("resident-a", "k-17", "repair"), first
        )
        self.assertEqual(len(service.records), 1)
        check_conflict_invariant(self, service)

    def test_req006_scopes_keys_to_principal(self):
        service = Atlas()
        a = service.create("resident-a", "k-17", "repair")
        b = service.create("resident-b", "k-17", "repair")
        self.assertNotEqual(a, b)
        self.assertEqual(len(service.records), 2)
        self.assertEqual(
            service.create("resident-a", "k-17", "repair"), a
        )
        self.assertEqual(
            service.create("resident-b", "k-17", "repair"), b
        )

    def test_spec_resolves(self):
        validate_spec(load_spec(), TestAtlas)

    def test_validator_rejects_dangling_link(self):
        spec = load_spec()
        spec["requirements"][0]["tests"] = ["test_not_present"]
        with self.assertRaises(ValueError):
            validate_spec(spec, TestAtlas)

    def test_counterexample_is_detected(self):
        broken = BrokenAtlas()
        with self.assertRaises(AssertionError):
            check_conflict_invariant(self, broken)


if __name__ == "__main__":
    unittest.main()
