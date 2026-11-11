# Chapter 12 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

### Purpose and status

Design a proposed Atlas extension with `REQ-006`: **an idempotency key must be a non-blank ASCII string of at most 32 characters**. This is a new authorial teaching policy, not an existing Atlas requirement or an approved v1.2 history. It applies to both new submissions and replays. Keys are compared literally; the exercise does not trim or normalise them.

The following files provide a self-contained **design exercise**. They are not claimed to exist in the canonical repository, and no test outcome is asserted here. Create them in a new directory such as `atlas_ch12_proposal`. The code deliberately uses a small independent model rather than silently modifying the Chapter 03 fixture. A real migration of that fixture would also require the version gate, expected identifiers, capture metadata and tests described in its README to be updated and reviewed.

### 1. Proposed specification

Create `spec.json`:

```json
{
  "version": "1.2-proposed",
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
      "invariant": "Keys are non-blank ASCII strings of at most 32 characters.",
      "tests": ["test_req006_key_boundaries"]
    }
  ]
}
```

This proposal retains the Chapter 03 test names for `REQ-001`–`REQ-005`, but supplies new implementations of those tests below. Equal names do not establish identical assertions or identical behaviour across fixtures.

### 2. Proposed model and structural validator

Create `atlas.py`:

```python
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
```

The validator checks a restricted structure and whether names appear in the supplied set. It does not establish that a test executes, asserts the invariant or checks policy. The model is deliberately single-instance and in-memory; it does not implement a network API.

### 3. Proposed acceptance and structural tests

Create `test_atlas.py`:

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
        self.assertEqual(api.submit("appointment", "b"),
                         ("R2", "submitted"))
        with self.assertRaises(ValueError):
            api.submit("other", "c")

    def test_req002_replays_and_rejects_conflict(self):
        api = Atlas()
        first = api.submit("permit", "a")
        self.assertEqual(api.submit("permit", "a"), first)
        with self.assertRaises(ValueError):
            api.submit("appointment", "a")
        self.assertEqual(api.submit("permit", "a"), first)

    def test_req003_enforces_ordered_lifecycle(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")
        self.assertEqual(api.advance("R1", "decided", "reviewer"),
                         "decided")
        with self.assertRaises(ValueError):
            api.advance("R1", "submitted", "reviewer")

    def test_req004_blocks_unauthorised_advancement(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "resident")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))

    def test_req005_replay_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.advance("R1", "under_review", "reviewer")
        self.assertEqual(api.submit("permit", "a"),
                         ("R1", "under_review"))
        api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "decided"))

    def test_req006_key_boundaries(self):
        api = Atlas()
        key = "a" * 32
        self.assertEqual(api.submit("permit", key), ("R1", "submitted"))
        self.assertEqual(api.submit("permit", key), ("R1", "submitted"))
        for invalid in ("", "  ", "a" * 33, "café"):
            with self.subTest(key=invalid):
                with self.assertRaises(ValueError):
                    api.submit("permit", invalid)
        self.assertEqual(api.submit("appointment", "b"),
                         ("R2", "submitted"))


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

The boundary test checks a 32-character key, a replay, several invalid keys and the next allocated identifier. The final assertion helps detect accidental allocation by rejected submissions. It does not exhaust every possible ASCII string, nor does it establish concurrent safety.

### 4. Execute and record

From the new directory, use Python 3.9 or later:

```bash
python --version
python -m unittest -v
python -c "import hashlib; from pathlib import Path; \
files = ['spec.json', 'atlas.py', 'test_atlas.py']; \
[(print(f, hashlib.sha256(Path(f).read_bytes()).hexdigest())) \
 for f in files]"
```

Record the interpreter version, complete test output, process exit status, hashes and execution date. If the suite fails, retain the failure and repair the proposal before making a new record. The acceptance target is a successful deterministic run for these files; it is not a result claimed in advance.

As a negative control, change the first specification link to `test_missing` and run the suite again. The structural resolution test should then report an error. Restore the file and rerun before recording final hashes. This manual alteration is distinct from the included test that checks whether `validate_spec` raises an error for a copied, deliberately broken specification.

Finally, ask a designated reviewer to record whether the new key policy is approved, rejected or undecided, with a rationale and scope. A passing suite alone leaves that decision **undecided**.
