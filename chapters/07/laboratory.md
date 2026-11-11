# Chapter 07 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This laboratory uses Python’s standard library and synthetic data. It requires no existing repository or LLM service. Create a new directory, enter it, and save the four files below exactly as shown. The expected test outcomes are specified for reproduction; they are not a claim that the code has been run in your environment.

### 1. Define both specification versions

Save as `baseline.json`:

```json
{
  "version": "1.0",
  "requirements": [
    {
      "id": "REQ-001",
      "name": "Request kind",
      "invariant": "Only maintenance is accepted.",
      "tests": ["test_req001_kind"]
    },
    {
      "id": "REQ-002",
      "name": "Idempotent submission",
      "invariant": "Same-key replay preserves the record; a different kind conflicts.",
      "tests": ["test_req002_replay", "test_req002_conflict"]
    },
    {
      "id": "REQ-003",
      "name": "Review transition",
      "invariant": "A submitted record can move to reviewed.",
      "tests": ["test_req003_transition"]
    },
    {
      "id": "REQ-004",
      "name": "Reviewer gate",
      "invariant": "Review requires the reviewer flag.",
      "tests": ["test_req004_reviewer"]
    }
  ]
}
```

Save as `spec.json`:

```json
{
  "version": "1.1",
  "requirements": [
    {
      "id": "REQ-001",
      "name": "Request kind",
      "invariant": "Only maintenance is accepted.",
      "tests": ["test_req001_kind"]
    },
    {
      "id": "REQ-002",
      "name": "Replay consistency",
      "invariant": "Same-key replay preserves the record; a different kind conflicts.",
      "tests": [
        "test_req002_replay_preserves_record",
        "test_req002_conflict_rejected"
      ]
    },
    {
      "id": "REQ-003",
      "name": "Review transition",
      "invariant": "A submitted record can move to reviewed.",
      "tests": ["test_req003_transition"]
    },
    {
      "id": "REQ-004",
      "name": "Reviewer gate",
      "invariant": "Review requires the reviewer flag.",
      "tests": ["test_req004_reviewer"]
    },
    {
      "id": "REQ-005",
      "name": "Description boundary",
      "invariant": "Reject non-string or blank descriptions before submission; otherwise forward arguments unchanged.",
      "tests": ["test_req005_description_boundary"]
    }
  ]
}
```

The text is intentionally concise. Its executable interpretation is supplied by the implementation and tests; an authorised reviewer would still need to assess whether that interpretation captures the intended policy.

### 2. Implement Atlas and the structural validator

Save as `atlas.py`:

```python
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
```

`validate_migration` is specific to this teaching migration. It compares two supplied documents; it cannot prove that the baseline itself was authorised or unaltered. Retain and compare the baseline hash as part of review.

### 3. Add behavioural and structural tests

Save as `test_atlas.py`:

```python
import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from atlas import Atlas, validate_migration, validate_spec, with_description


ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class TestAtlas(unittest.TestCase):
    def setUp(self):
        self.api = Atlas()

    def test_req001_kind(self):
        with self.assertRaises(ValueError):
            self.api.submit("A-1", "unsupported")
        self.assertEqual(self.api.records, {})

    def test_req002_replay_preserves_record(self):
        first = self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        replay = self.api.submit("A-1", "maintenance")
        self.assertEqual(replay, first)
        self.assertEqual(self.api.records, before)

    def test_req002_conflict_rejected(self):
        self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        with self.assertRaises(ValueError):
            self.api.submit("A-1", "other")
        self.assertEqual(self.api.records, before)

    # Preserve the two v1.0 link names as aliases to the same test bodies.
    test_req002_replay = test_req002_replay_preserves_record
    test_req002_conflict = test_req002_conflict_rejected

    def test_req003_transition(self):
        self.api.submit("A-1", "maintenance")
        result = self.api.review("A-1", reviewer=True)
        self.assertEqual(result["status"], "reviewed")

    def test_req004_reviewer(self):
        self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        with self.assertRaises(PermissionError):
            self.api.review("A-1", reviewer=False)
        self.assertEqual(self.api.records, before)

    def test_req005_description_boundary(self):
        with patch.object(self.api, "submit", wraps=self.api.submit) as submit:
            guarded = with_description(submit)
            result = guarded("Repair a bench", "A-1", kind="maintenance")
            self.assertEqual(result["status"], "submitted")
            submit.assert_called_once_with("A-1", kind="maintenance")

            before = deepcopy(self.api.records)
            submit.reset_mock()
            for invalid in ("", "   ", "\t", None, 42):
                with self.subTest(description=invalid):
                    with self.assertRaises(ValueError):
                        guarded(invalid, "A-2", kind="maintenance")
                    submit.assert_not_called()
                    self.assertEqual(self.api.records, before)


class TestSpecification(unittest.TestCase):
    def test_versions_and_migration(self):
        baseline, proposed = load("baseline.json"), load("spec.json")
        validate_spec(
            baseline, "1.0",
            {"REQ-001", "REQ-002", "REQ-003", "REQ-004"},
            TestAtlas,
        )
        validate_spec(
            proposed, "1.1",
            {"REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"},
            TestAtlas,
        )
        validate_migration(baseline, proposed)

    def test_dangling_link_is_rejected(self):
        proposed = load("spec.json")
        proposed["requirements"][-1]["tests"] = ["test_missing"]
        with self.assertRaisesRegex(ValueError, "unresolved test link"):
            validate_spec(
                proposed, "1.1",
                {"REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"},
                TestAtlas,
            )


if __name__ == "__main__":
    unittest.main()
```

Run:

```bash
python -m unittest -v test_atlas
```

The expected result is ten passing test methods. The old and new REQ-002 names each run the same two bodies: this provides link compatibility, not four independent behavioural cases. The dangling-link test modifies an in-memory copy, so it does not leave the specification file damaged.

### 4. Capture a local record

Save as `capture.py`:

```python
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = ["baseline.json", "spec.json", "atlas.py", "test_atlas.py", "capture.py"]


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in FILES
    }


before = hashes()
command = [sys.executable, "-m", "unittest", "-v", "test_atlas"]
run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
after = hashes()

record = {
    "scope": "Synthetic in-memory Atlas laboratory",
    "interpreter": sys.version,
    "command": command,
    "exit_status": run.returncode,
    "stdout": run.stdout,
    "stderr": run.stderr,
    "hashes_before": before,
    "hashes_after": after,
    "inputs_unchanged_during_run": before == after,
    "policy_approval": "not recorded",
}
(ROOT / "run-record.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
print("Wrote run-record.json")
sys.exit(0 if run.returncode == 0 and before == after else 1)
```

Run `python capture.py`, inspect `run-record.json`, and retain it with the files examined. A successful record should show exit status zero and unchanged input hashes. The record identifies local bytes and output; it is not a signed provenance statement. An authorised policy decision, including reviewer identity, scope and date, must be recorded separately through an appropriate process.

### 5. Challenge the evidence

Temporarily change `with_description` so it calls `submit(*args, **kwargs)` **before** checking the description. Run the tests: the REQ-005 case should fail because the mock observes delegation for invalid input. Restore the wrapper and rerun `capture.py`.

Next, replace the REQ-005 link in a temporary copy of `spec.json` with `test_req001_kind`. It resolves, but tests a different obligation. The structural gate alone cannot detect that semantic mismatch. Restore the link before the final run.

The laboratory covers selected in-memory cases. It does not establish HTTP correctness, persistence, concurrency safety, identity verification, privacy, accessibility or enforcement at every call site.
