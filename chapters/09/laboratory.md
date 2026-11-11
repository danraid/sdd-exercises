# Chapter 09 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

### Status and purpose

The canonical repository contains the complete Chapter 03 v1.1 fixture, including `examples/atlas_ch03/atlas.py`, `spec.json`, `test_atlas.py` and `capture.py`. The files below define a **separate proposed extension**, not a patch already installed or executed in that canonical directory. No result for this proposed extension is asserted.

The exercise reconstructs a small implementation of the Chapter 03 API interface and extends its own model with `REQ-006`. It uses the same request kinds, `R1`-style identifiers, lifecycle and instructional role placeholder, but its implementation is not byte-identical to the separately available Chapter 03 `atlas.py`. To turn this proposal into a canonical extension, compare and integrate the changes in a versioned branch, run the existing and new tests, and retain the observed evidence.

The role string is an instructional placeholder, not authentication.

### 1. Create the specification

Create a new empty working directory. Save the following as `spec-v1.1.json`. The five requirement objects and links reproduce the supplied Chapter 03 specification.

```json
{
  "version": "1.1",
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
    }
  ]
}
```

Save this candidate generator as `prepare.py`:

```python
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NEW_REQUIREMENT = {
    "id": "REQ-006",
    "invariant": (
        "A conflicting key reuse leaves records, key bindings and "
        "the next request identifier unchanged."
    ),
    "tests": ["test_req006_conflict_preserves_state"],
}


def make_candidate(base):
    if base.get("version") != "1.1":
        raise ValueError("expected the supplied v1.1 specification")
    requirements = base.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
    if any(item.get("id") == "REQ-006" for item in requirements):
        raise ValueError("REQ-006 already exists")

    candidate = copy.deepcopy(base)
    candidate["version"] = "1.2"
    candidate["requirements"].append(copy.deepcopy(NEW_REQUIREMENT))
    return candidate


if __name__ == "__main__":
    base = json.loads((ROOT / "spec-v1.1.json").read_text(encoding="utf-8"))
    candidate = make_candidate(base)
    (ROOT / "spec.json").write_text(
        json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
    )
```

The generator copies the supplied requirement objects and links, then adds the candidate requirement. The preservation test below checks that construction mechanically; it does not prove semantic equivalence between v1.0 and v1.1 tests.

### 2. Implement the teaching model and validator

Save as `atlas.py`:

```python
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
```

The validator checks the candidate’s version, identifiers, non-empty invariants and test names. It does not inspect assertions or authorise policy. Its version gate belongs to this reconstructed exercise and does not modify the separate Chapter 03 implementation.

### 3. Add the acceptance and structural tests

Save as `test_atlas.py`. The first five methods preserve the supplied Chapter 03 behavioural assertions. The new method tests the candidate invariant.

```python
import copy
import json
from pathlib import Path
import unittest

from atlas import Atlas, validate_spec
from prepare import make_candidate


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

    def test_req006_conflict_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.submit("appointment", "b")
        api.advance("R1", "under_review", "reviewer")
        before = api.snapshot()

        with self.assertRaises(ValueError):
            api.submit("appointment", "a")

        self.assertEqual(api.snapshot(), before)
        self.assertEqual(api.submit("permit", "a"), ("R1", "under_review"))
        self.assertEqual(api.submit("permit", "c"), ("R3", "submitted"))


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent
        self.spec = json.loads((root / "spec.json").read_text(encoding="utf-8"))
        self.base = json.loads(
            (root / "spec-v1.1.json").read_text(encoding="utf-8")
        )
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

    def test_candidate_preserves_baseline(self):
        self.assertEqual(self.spec, make_candidate(self.base))
        self.assertEqual(
            self.spec["requirements"][:-1], self.base["requirements"]
        )


if __name__ == "__main__":
    unittest.main()
```

The Chapter 03 structural tests in the repository check link resolution and a dangling link. Here those patterns are adapted for the candidate, and a baseline-preservation check is added. The behavioural tests exercise the separately written model, not the canonical Chapter 03 `atlas.py`.

### 4. Capture a run

Save as `capture.py`:

```python
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
INPUTS = [
    "spec-v1.1.json", "spec.json", "prepare.py",
    "atlas.py", "test_atlas.py", "capture.py",
]


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in INPUTS
    }


if __name__ == "__main__":
    before = hashes()
    command = [sys.executable, "-m", "unittest", "-v", "test_atlas"]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    after = hashes()
    record = {
        "scope": "Reconstructed sequential Atlas model and candidate REQ-006",
        "python": sys.version,
        "command": command,
        "input_sha256_before": before,
        "input_sha256_after": after,
        "inputs_unchanged": before == after,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "policy_approval": "not recorded",
    }
    (ROOT / "run-record.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    sys.exit(0 if result.returncode == 0 and before == after else 1)
```

After creating the files, generate the candidate and attempt the checks:

```bash
python prepare.py
python capture.py
```

Inspect `run-record.json`, including the test output, exit code and before-and-after hashes. A successful local run would be bounded evidence for those files and exercised cases. The record does not attest interpreter integrity or prove that a file was not changed and restored during execution. It records no policy approval.

For a sensitivity check, temporarily add the reset shown in the counterexample to the conflict branch. The exception-only assertion should still be satisfied, while `test_req006_conflict_preserves_state` should fail on the snapshot comparison. Restore the implementation and capture a fresh run; do not use the earlier record as evidence for changed bytes.

The chapter’s deterministic-test acceptance condition remains **unverified** until the files are installed in the canonical repository and the checks are actually executed. Even then, a passing run would not establish concurrency safety, HTTP behaviour, persistence, identity verification, privacy or accessibility.
