# Chapter 03 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This laboratory implements the author-created v1.1 extension using Python’s standard library. It is a deterministic, single-process model, not a network service. Its role string is an instructional placeholder, not authentication.

### Traceability from v1.0

The v1.0 specification and its executable acceptance tests are stored under `examples/atlas_ch01/` in this repository. The v1.1 extension used in this chapter is stored in `examples/atlas_ch03/` and provides an explicit migration table rather than silently renaming previous tests. In particular, the two v1.0 `REQ-002` tests are combined into one method that checks both replay and conflict. Thus the new artefact has **five** Atlas test methods and **two** specification-validator test methods.

| v1.0 acceptance link | v1.1 laboratory link |
|---|---|
| `test_req001_accepts_only_declared_request_kinds` | Same name |
| `test_req002_replays_idempotently` | `test_req002_replays_and_rejects_conflict` |
| `test_req002_rejects_conflicting_replay` | `test_req002_replays_and_rejects_conflict` |
| `test_req003_enforces_ordered_lifecycle` | Same name |
| `test_req004_blocks_unauthorised_advancement` | Same name |
| No v1.0 link for `REQ-005` | `test_req005_replay_preserves_state` |

This mapping updates trace links; it does not assert that the unavailable earlier test files were run or prove that the replacement tests are semantically identical to them.

The following four files are versioned together at `examples/atlas_ch03/`. For a stand-alone exercise, copy them into an empty directory or inspect the repository originals rather than transcribing the code from the printed book.

**`spec.json`**

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

**`atlas.py`**

```python
"""Synthetic, single-process Atlas teaching model."""

EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 6)}
KINDS = {"permit", "appointment"}
NEXT = {"submitted": "under_review", "under_review": "decided"}


def validate_spec(spec, available_tests):
    """Check specification structure and named test links."""
    if not isinstance(spec, dict) or spec.get("version") != "1.1":
        raise ValueError("expected specification version 1.1")
    if not isinstance(spec.get("scope"), str) or not spec["scope"].strip():
        raise ValueError("missing scope")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = set()
    for req in requirements:
        if not isinstance(req, dict):
            raise ValueError("requirement must be an object")
        rid = req.get("id")
        if not isinstance(rid, str) or rid in ids:
            raise ValueError("missing or duplicate requirement ID")
        ids.add(rid)

        invariant = req.get("invariant")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError(f"{rid}: missing invariant")
        tests = req.get("tests")
        if not isinstance(tests, list) or not tests:
            raise ValueError(f"{rid}: missing test links")
        for name in tests:
            if not isinstance(name, str) or name not in available_tests:
                raise ValueError(f"{rid}: unresolved test link")

    if ids != EXPECTED_IDS:
        raise ValueError("unexpected requirement IDs")


class Atlas:
    def __init__(self):
        self._by_key = {}
        self._by_id = {}
        self._next_id = 1

    def submit(self, kind, key):
        if kind not in KINDS:
            raise ValueError("invalid kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be non-blank")

        if key in self._by_key:
            record = self._by_key[key]
            if record["kind"] != kind:
                raise ValueError("conflicting key reuse")
            return record["id"], record["state"]

        request_id = f"R{self._next_id}"
        self._next_id += 1
        record = {"id": request_id, "kind": kind, "state": "submitted"}
        self._by_key[key] = record
        self._by_id[request_id] = record
        return request_id, record["state"]

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer role required")
        record = self._by_id[request_id]  # Unknown IDs raise KeyError.
        if NEXT.get(record["state"]) != target or target is None:
            raise ValueError("invalid transition")
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

The validator checks that required IDs and non-empty invariants exist and that named methods are discoverable. This is only **structural link resolution**: it does not determine whether the prose is correct, whether a test's assertions correspond to its named requirement, or whether the behaviour and policy are appropriate. The separate `AtlasTests` methods provide bounded behavioural checks. Neither group of tests records the external policy approval required for a release decision.

**`capture.py`**

```python
"""Capture a test run and the bytes of its input artefacts."""

import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
FILES = ("spec.json", "atlas.py", "test_atlas.py", "capture.py")


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in FILES
    }


before = hashes()
command = [
    sys.executable, "-m", "unittest", "discover",
    "-s", ".", "-p", "test_atlas.py", "-v"
]
run = subprocess.run(
    command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    errors="replace"
)
after = hashes()
unchanged = before == after

lines = [
    "Atlas laboratory acceptance evidence",
    "Specification version: 1.1",
    f"Python executable: {sys.executable}",
    f"Python version: {sys.version}",
    f"Command arguments: {command!r}",
    f"Working directory: {ROOT}",
    f"Test exit status: {run.returncode}",
    f"Input hashes unchanged across run: {unchanged}",
    "SHA-256 before run:",
]
lines.extend(f"  {name}: {digest}" for name, digest in before.items())
lines.append("SHA-256 after run:")
lines.extend(f"  {name}: {digest}" for name, digest in after.items())
lines.extend([
    "--- standard output ---",
    run.stdout,
    "--- standard error ---",
    run.stderr,
    "--- decision ---",
    "PENDING: authorised reviewer must record decision separately.",
])
record = "\n".join(lines) + "\n"
(ROOT / "run-record.txt").write_text(record, encoding="utf-8")
print(record)
sys.exit(0 if run.returncode == 0 and unchanged else 1)
```

From the directory containing the files, run:

```sh
python capture.py
```

The expected result is **seven tests passing**: five `AtlasTests` and two `SpecificationTests`. The script writes `run-record.txt`, captures the actual output and test exit status, and records hashes before and after execution. Output formatting and elapsed time may vary. A non-zero test status or changed input hash makes the capture script exit non-zero.

Review the actual run record rather than copying an expected result into it. First record the **stakeholder policy decision** separately, identifying the person or role with authority to approve the replay-state requirement. Only then should an authorised reviewer combine that signed policy decision with the structural and behavioural evidence to decide whether to accept the specified laboratory artefacts. No Python test automates either of these human decisions. For example:

```text
Atlas v1.1 decision
Run record reviewed: run-record.txt
Decision: ACCEPT / REJECT / PENDING
Policy approval reference (external to tests):
Policy approved by (authorised stakeholder):
Policy approval date:
Reviewer / decision-maker:
Review date:
Reason and limitations:
```

For acceptance, the decision-maker should identify the reviewed run record and confirm the policy and scope as well as the test result. Preserve both files with the artefacts; hash or otherwise protect the record if it is transferred. Hashing before and after a run detects persistent byte changes, not every possible transient modification or environmental influence.

### Negative control

Preserve the passing record under another name. Then temporarily insert this line immediately before the valid-replay `return` in `Atlas.submit`:

```python
record["state"] = "submitted"
```

Run `python capture.py` again. The combined `REQ-002` test still passes: it replays while the request is initially `submitted`. `test_req005_replay_preserves_state` fails after advancement, so the capture script exits non-zero. Preserve this negative-control record if required, remove the inserted line, rerun the capture and verify that all seven tests pass again.

The negative control demonstrates sensitivity to one defect, not complete coverage. The model does not test races, durability or real authorisation, and the validator does not establish stakeholder approval. Those limitations belong in the decision record.
