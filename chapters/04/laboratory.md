# Chapter 04 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This original laboratory is versioned under `examples/atlas_ch04/` and uses synthetic data and Python's standard library. It assumes Python 3.10 or later, a sequential caller, one process and no direct external mutation of internal dictionaries. The four files below are included in the repository for reproducibility; do not confuse their trace manifest with the canonical `examples/atlas_ch03/` example. Use the migration table in `examples/atlas_ch04/README.md` to audit which earlier obligations were renamed or combined before accepting a change.

### 1. Versioned specification: `spec.json`

```json
{
  "name": "Synthetic Atlas API",
  "version": "1.1",
  "test_class": "TestAtlasAcceptance",
  "requirements": {
    "REQ-001": [
      "test_req001_declared_kinds"
    ],
    "REQ-002": [
      "test_req002_replay_preserves_progress",
      "test_req002_conflicting_replay_rejected"
    ],
    "REQ-003": [
      "test_req003_ordered_lifecycle"
    ],
    "REQ-004": [
      "test_req004_reviewer_only"
    ]
  }
}
```

This is a trace manifest, not a complete formal specification. Its version identifies the teaching artefact described in the worked example.

### 2. Implementation: `atlas.py`

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Record:
    kind: str
    state: str


class Atlas:
    KINDS = {"permit", "appointment"}
    NEXT = {
        "submitted": "under_review",
        "under_review": "decided",
    }

    def __init__(self):
        self._keys = {}
        self._records = {}
        self._next_id = 1

    def submit(self, key, kind):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-blank string")
        if kind not in self.KINDS:
            raise ValueError("unknown kind")

        if key in self._keys:
            request_id = self._keys[key]
            if self._records[request_id].kind != kind:
                raise ValueError("conflicting replay")
            return request_id

        request_id = self._next_id
        self._next_id += 1
        self._keys[key] = request_id
        self._records[request_id] = Record(kind, "submitted")
        return request_id

    def get(self, request_id):
        return self._records[request_id]

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer role required")
        record = self._records[request_id]
        if self.NEXT.get(record.state) != target:
            raise ValueError("invalid transition")
        self._records[request_id] = replace(record, state=target)
```

Keys are compared exactly: whitespace-only keys are rejected, but leading or trailing whitespace in a non-blank key is not normalised. The specification and tests must change together if a different interpretation is agreed. `Record` is immutable, but the dictionaries are still accessible Python attributes; the contract assumes callers do not mutate them directly.

### 3. Tests: `test_atlas.py`

```python
import unittest
from dataclasses import replace

from atlas import Atlas


class ResetOnReplayAtlas(Atlas):
    """Intentional mutant for the negative control only."""

    def submit(self, key, kind):
        existed = key in self._keys
        request_id = super().submit(key, kind)
        if existed:
            self._records[request_id] = replace(
                self._records[request_id], state="submitted"
            )
        return request_id


class TestAtlasAcceptance(unittest.TestCase):
    def test_req001_declared_kinds(self):
        api = Atlas()
        self.assertEqual(api.get(api.submit("a", "permit")).kind, "permit")
        self.assertEqual(
            api.get(api.submit("b", "appointment")).kind, "appointment"
        )
        with self.assertRaises(ValueError):
            api.submit("c", "licence")
        with self.assertRaises(ValueError):
            api.submit("   ", "permit")

    def test_req002_replay_preserves_progress(self):
        api = Atlas()
        request_id = api.submit("key-1", "permit")
        api.advance(request_id, "under_review", "reviewer")
        before = api.get(request_id)

        replay_id = api.submit("key-1", "permit")

        self.assertEqual(replay_id, request_id)
        self.assertEqual(api.get(request_id), before)

    def test_req002_conflicting_replay_rejected(self):
        api = Atlas()
        request_id = api.submit("key-2", "permit")
        before = api.get(request_id)
        with self.assertRaises(ValueError):
            api.submit("key-2", "appointment")
        self.assertEqual(api.get(request_id), before)
        self.assertEqual(api.submit("key-2", "permit"), request_id)

    def test_req003_ordered_lifecycle(self):
        api = Atlas()
        request_id = api.submit("key-3", "permit")
        with self.assertRaises(ValueError):
            api.advance(request_id, "decided", "reviewer")
        self.assertEqual(api.get(request_id).state, "submitted")

        api.advance(request_id, "under_review", "reviewer")
        api.advance(request_id, "decided", "reviewer")
        self.assertEqual(api.get(request_id).state, "decided")
        with self.assertRaises(ValueError):
            api.advance(request_id, "submitted", "reviewer")
        self.assertEqual(api.get(request_id).state, "decided")

    def test_req004_reviewer_only(self):
        api = Atlas()
        request_id = api.submit("key-4", "appointment")
        with self.assertRaises(PermissionError):
            api.advance(request_id, "under_review", "resident")
        self.assertEqual(api.get(request_id).state, "submitted")


class TestNegativeControl(unittest.TestCase):
    def test_identity_only_misses_reset(self):
        api = ResetOnReplayAtlas()
        request_id = api.submit("mutant-key", "permit")
        api.advance(request_id, "under_review", "reviewer")

        replay_id = api.submit("mutant-key", "permit")

        self.assertEqual(replay_id, request_id)  # Shallow check passes.
        self.assertEqual(api.get(request_id).state, "submitted")
        # The second assertion demonstrates the defect; it is not approval.


if __name__ == "__main__":
    unittest.main()
```

### 4. Structural validator: `validate.py`

```python
import ast
import json
import sys
from pathlib import Path


def validate():
    spec = json.loads(Path("spec.json").read_text(encoding="utf-8"))
    if spec.get("version") != "1.1":
        raise ValueError("expected Atlas specification version 1.1")

    requirements = spec.get("requirements")
    expected = {"REQ-001", "REQ-002", "REQ-003", "REQ-004"}
    if not isinstance(requirements, dict) or set(requirements) != expected:
        raise ValueError("missing or unexpected requirement identifiers")

    tree = ast.parse(Path("test_atlas.py").read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == spec.get("test_class")
    ]
    if len(classes) != 1:
        raise ValueError("expected exactly one named test class")

    methods = [
        node.name for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) != len(set(methods)):
        raise ValueError("duplicate test method name")

    for req, names in requirements.items():
        if not isinstance(names, list) or not names:
            raise ValueError(f"{req}: expected a non-empty test list")
        if any(not isinstance(name, str) or not name.startswith("test_")
               for name in names):
            raise ValueError(f"{req}: invalid test name")
        if len(names) != len(set(names)):
            raise ValueError(f"{req}: duplicate test reference")
        missing = set(names) - set(methods)
        if missing:
            raise ValueError(f"{req}: unresolved names {sorted(missing)}")

    print("STRUCTURAL PASS: declared test names resolve; tests not run.")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        print(f"STRUCTURAL FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
```

From that directory, run:

```sh
python --version
python validate.py
python -m unittest -v
```

The intended structural result is the printed `STRUCTURAL PASS` message. The intended behavioural result is six passing tests: five acceptance methods and one negative-control demonstration. Record the actual output rather than assuming it occurred. A non-zero exit, missing test or unexpected count requires investigation.

For an intentional failing experiment, temporarily replace the construction `api = Atlas()` **only inside** `test_req002_replay_preserves_progress` with `api = ResetOnReplayAtlas()`, then run:

```sh
python -m unittest -v \
  test_atlas.TestAtlasAcceptance.test_req002_replay_preserves_progress
```

The ID assertion should pass, but the record-equality assertion should fail because the mutant resets the state. Restore `Atlas()`, rerun both gates and record the restored result. Do not treat the intentionally failing mutant run as evidence about the unmodified implementation.

Finally, record the specification version, Python version, commands, outcomes and identities of all four files. For example, file hashes can be produced portably from Python:

```sh
python -c "import hashlib,pathlib; [(print(p, hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest())) for p in ('spec.json','atlas.py','test_atlas.py','validate.py')]"
```

A passing validator and suite support only the artefacts and cases recorded. The structural validator **does not** check that a test asserts its named obligation; the behavioural suite only exercises selected cases. A human must review the actual assertions against the approved requirement and separately record the policy authorisation. Neither an observed green test suite nor the placeholder `reviewer` role is a policy approval. Production security, persistence, accessibility and resilience remain outside the synthetic scope.
