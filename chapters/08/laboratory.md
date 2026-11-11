# Chapter 08 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

### Scope and setup

This laboratory is a standalone, author-created reconstruction of the Atlas behaviours relevant to this chapter. It does not import or validate an earlier Atlas fixture. Its `1.2-lab` label identifies these local teaching files; it does not assert that the complete Atlas specification has been migrated. Python 3 is sufficient, with no third-party packages.

Create an empty directory and save the following as `spec.json`:

```json
{
  "version": "1.2-lab",
  "requirements": [
    {
      "id": "REQ-002",
      "invariant": "A conflicting replay leaves stored state unchanged.",
      "tests": ["test_req002_replays_and_rejects_conflict"]
    },
    {
      "id": "REQ-006",
      "invariant": "Idempotency keys are scoped to the supplied principal.",
      "tests": ["test_req006_scopes_keys_to_principal"]
    }
  ]
}
```

Save the following as `atlas_lab.py` in the same directory:

```python
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
```

Run the tests from that directory:

```bash
python -VV
python -m unittest -v atlas_lab
```

The objective check is that **five test methods pass** and the test command exits with status zero. The counterexample test passes because it expects the stronger invariant check to fail against `BrokenAtlas`; it does not mean that the broken implementation is acceptable. `BrokenAtlas` raises the expected `ValueError` even though it changes `records`.

For a local run record, capture the input hashes before and after execution, the Python version, full test output and exit status. For example, in a shell with `sha256sum`:

```bash
sha256sum spec.json atlas_lab.py > run-record.txt
python -VV >> run-record.txt 2>&1
python -m unittest -v atlas_lab >> run-record.txt 2>&1
status=$?
echo "test exit status: $status" >> run-record.txt
sha256sum spec.json atlas_lab.py >> run-record.txt
cat run-record.txt
```

Inspect the recorded status rather than assuming success from the final `cat` command. Matching pre- and post-run hashes support identification of the input bytes at those two times; they do not prove that the files were unchanged throughout execution or provide a tamper-proof provenance chain. On platforms without `sha256sum`, use an equivalent SHA-256 utility and record which utility was used.

### Interpreting the gates

The structural tests show whether the local validator accepts the listed IDs and resolves the named methods, and whether it rejects one deliberately dangling name. The validator does not inspect assertions or establish semantic coverage. Its hard-coded version and ID set must be changed when this local specification evolves.

The behavioural tests execute selected in-memory cases. They do not demonstrate that a real client cannot forge a principal, that simultaneous creates are safe, or that receipts survive process restarts. The code is a teaching component, not an HTTP service or production-ready implementation.

Finally, write a separate policy decision record. For this exercise, use **“not approved: no authorised reviewer has decided”** unless an actual authorised reviewer has made and recorded a decision for the intended context. Do not infer approval from the test output.

Extending the repository's canonical `examples/atlas_ch03/` implementation is a different task. It requires inspecting the actual specification, implementation, test assertions and change history, then recording evidence for the changed bytes. A passing result from this stand-alone reconstruction does not validate the canonical Atlas fixture.
