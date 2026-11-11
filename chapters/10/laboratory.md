# Chapter 10 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

### Scope and preparation

This is a **design exercise for a proposed extension**, not an already merged or executed Chapter 10 laboratory. The repository contains the complete Chapter 03 baseline, but not the proposed `REQ-006` extension. The teaching files below allow a reader to construct an independent local model and attempt the checks; no execution outcome for these proposed files is asserted here.

Use a new, empty local directory and Python 3. The specification retains the Chapter 03 requirement identifiers and test links, then adds `REQ-006`. The reconstructed tests use those names but are not claimed to be byte-identical to, or a verified migration of, the dossier’s tests.

**`spec.json`**

```json
{
  "version": "1.2-ch10-proposal",
  "scope": "One synthetic in-memory Atlas instance",
  "requirements": [
    {
      "id": "REQ-001",
      "invariant": "Only permit and appointment kinds are accepted.",
      "tests": ["test_req001_accepts_only_declared_request_kinds"]
    },
    {
      "id": "REQ-002",
      "invariant": "Matching keys and kinds retain identity; conflicts fail.",
      "tests": ["test_req002_replays_and_rejects_conflict"]
    },
    {
      "id": "REQ-003",
      "invariant": "Only the next lifecycle state is permitted.",
      "tests": ["test_req003_enforces_ordered_lifecycle"]
    },
    {
      "id": "REQ-004",
      "invariant": "Only the reviewer role advances state.",
      "tests": ["test_req004_blocks_unauthorised_advancement"]
    },
    {
      "id": "REQ-005",
      "invariant": "A valid replay preserves and returns current state.",
      "tests": ["test_req005_replay_preserves_state"]
    },
    {
      "id": "REQ-006",
      "invariant": "For an existing request, advancement rejected for an unauthorised role or illegal transition leaves all in-memory state unchanged.",
      "tests": ["test_req006_rejected_advancement_preserves_state"]
    }
  ]
}
```

**`atlas.py`**

```python
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
```

**`test_atlas.py`**

```python
import copy
import json
from pathlib import Path
import unittest

from atlas import Atlas, validate_spec


class AtlasTests(unittest.TestCase):
    def test_req001_accepts_only_declared_request_kinds(self):
        api = Atlas()
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.submit("appointment", "b"), ("R2", "submitted"))
        with self.assertRaises(ValueError):
            api.submit("other", "c")
        with self.assertRaises(ValueError):
            api.submit("permit", "  ")

    def test_req002_replays_and_rejects_conflict(self):
        api = Atlas()
        first = api.submit("permit", "a")
        self.assertEqual(api.submit("permit", "a"), first)
        with self.assertRaises(ValueError):
            api.submit("appointment", "a")
        self.assertEqual(api.submit("permit", "a"), first)
        self.assertEqual(api.submit("appointment", "b"), ("R2", "submitted"))

    def test_req003_enforces_ordered_lifecycle(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")
        self.assertEqual(api.advance("R1", "decided", "reviewer"), "decided")
        with self.assertRaises(ValueError):
            api.advance("R1", "submitted", "reviewer")

    def test_req004_blocks_unauthorised_advancement(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")

    def test_req005_replay_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.advance("R1", "under_review", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "under_review"))
        api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "decided"))

    def test_req006_rejected_advancement_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        before = api.snapshot()

        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.snapshot(), before)

        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.snapshot(), before)

        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("spec.json")
        self.spec = json.loads(path.read_text(encoding="utf-8"))
        self.available = set(
            unittest.defaultTestLoader.getTestCaseNames(AtlasTests)
        )

    def test_spec_links_resolve(self):
        validate_spec(self.spec, self.available)

    def test_spec_rejects_dangling_link(self):
        broken = copy.deepcopy(self.spec)
        broken["requirements"][0]["tests"] = ["test_missing"]
        with self.assertRaises(ValueError):
            validate_spec(broken, self.available)


if __name__ == "__main__":
    unittest.main()
```

The structural negative control changes a link in a copy of the specification and expects the validator to reject it; it does not modify the file. The `REQ-006` test observes the state exposed by this reconstruction’s `snapshot`, including the key map and identifier counter. Its positive reviewer transition also checks that the implementation does not simply reject every advancement.

### Attempt the checks and record evidence

After creating the files, use the following commands from the new directory:

```bash
python --version
python -m unittest -v
```

The intended outcome is that the deterministic tests pass, including the expected exceptions inside negative checks. This is an expectation for the reader to verify, not a reported execution result. Record the actual output and process exit status. For example, in a POSIX shell:

```bash
python --version > environment.txt 2>&1
python -m unittest -v > run-record.txt 2>&1
status=$?
printf 'test exit status: %s\n' "$status" >> run-record.txt
cat run-record.txt
sha256sum spec.json atlas.py test_atlas.py > input-hashes.txt
cat input-hashes.txt
```

Preserve the digests with the status and environment record. If a file changes, calculate its digest again and rerun the relevant checks: an earlier result no longer identifies the changed bytes. On a system without `sha256sum`, use an equivalent SHA-256 tool and record which tool was used.

To investigate the counterexample, work on a disposable copy of `atlas.py`: insert a state assignment before the role check in `advance`. Run the tests and inspect any failed state assertion. Restore the file and rerun before recording proposed acceptance evidence. The failure output is an observation for the reader’s execution, not a result asserted here.

A separate approval record should identify the artefact digests, execution record, intended use, reviewer’s authority, decision and unresolved limitations. No laboratory script should manufacture policy approval.
