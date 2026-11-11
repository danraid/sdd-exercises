# Chapter 06 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This laboratory creates a **complete synthetic fixture and a genuine extension of that fixture**. It does not modify the separately available Chapter 03 implementation. Its `LAB-*` requirements and data are author-created, and any integration into canonical Atlas must be inspected and tested independently.

Use Python 3 and create a new directory. Save the following files there.

### 1. Create the base specification

Save `base_spec.json`:

```json
{
  "version": "teaching-base-1",
  "requirements": [
    {
      "id": "LAB-001",
      "invariant": "A new submission receives an identifier.",
      "tests": ["test_lab001_create"]
    },
    {
      "id": "LAB-002",
      "invariant": "A matching replay returns the identifier; a conflicting payload is rejected without changing the record.",
      "tests": ["test_lab002_replay_and_conflict"]
    },
    {
      "id": "LAB-003",
      "invariant": "A snapshot exposes the stored identifier and payload.",
      "tests": ["test_lab003_snapshot"]
    },
    {
      "id": "LAB-004",
      "invariant": "A record can be marked reviewed.",
      "tests": ["test_lab004_review"]
    },
    {
      "id": "LAB-005",
      "invariant": "Distinct new keys receive distinct identifiers in sequential use.",
      "tests": ["test_lab005_distinct_ids"]
    }
  ]
}
```

These are fixture obligations, not assertions about the unseen reference specification.

### 2. Implement the base API, extension and validator

Save `atlas.py`:

```python
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
```

The restriction against reused links is deliberately local. A real test can legitimately support more than one requirement. Conversely, uniqueness here does not make a link meaningful.

### 3. Derive the extension

Save `extend.py`:

```python
import json
from copy import deepcopy
from pathlib import Path

from atlas import BASE_VERSION, EXTENDED_VERSION

HERE = Path(__file__).resolve().parent
base = json.loads((HERE / "base_spec.json").read_text(encoding="utf-8"))
if base.get("version") != BASE_VERSION:
    raise ValueError("unexpected base version")

spec = deepcopy(base)
spec["version"] = EXTENDED_VERSION
spec["requirements"].append({
    "id": "REQ-006",
    "invariant": (
        "In the sequential model, a matching replay returns the "
        "original identifier and preserves every stored field."
    ),
    "tests": ["test_req006_preserves_record"],
})
(HERE / "spec.json").write_text(
    json.dumps(spec, indent=2) + "\n", encoding="utf-8"
)
```

This is a visible fixture migration: unchanged base objects plus one new requirement. It makes no assertion about historical Atlas bytes.

### 4. Add acceptance and negative-control tests

Save `test_atlas.py`:

```python
import copy
import json
import unittest
from pathlib import Path

from atlas import Atlas, BaseAtlas, validate_spec

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class AtlasTests(unittest.TestCase):
    def test_lab001_create(self):
        self.assertEqual("A-1", Atlas().submit("k-17", "repair"))

    def test_lab002_replay_and_conflict(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        self.assertEqual(first, service.submit("k-17", "repair"))
        before = service.snapshot("k-17")
        with self.assertRaises(ValueError):
            service.submit("k-17", "housing")
        self.assertEqual(before, service.snapshot("k-17"))

    def test_lab003_snapshot(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        record = service.snapshot("k-17")
        self.assertEqual(first, record["id"])
        self.assertEqual("repair", record["payload"])

    def test_lab004_review(self):
        service = Atlas()
        service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        self.assertTrue(service.snapshot("k-17")["reviewed"])

    def test_lab005_distinct_ids(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        second = service.submit("k-18", "housing")
        self.assertNotEqual(first, second)

    def test_req006_preserves_record(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        before = service.snapshot("k-17")
        self.assertEqual(first, service.submit("k-17", "repair"))
        self.assertEqual(before, service.snapshot("k-17"))
        with self.assertRaises(ValueError):
            service.submit("k-17", "housing")
        self.assertEqual(before, service.snapshot("k-17"))

    def test_shallow_check_misses_defect(self):
        service = BaseAtlas()
        first = service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        before = service.snapshot("k-17")
        self.assertEqual(first, service.submit("k-17", "repair"))
        self.assertNotEqual(before, service.snapshot("k-17"))
        self.assertFalse(service.snapshot("k-17")["reviewed"])

    def test_spec_links_resolve(self):
        validate_spec(load("base_spec.json"), load("spec.json"), AtlasTests)

    def test_dangling_link_rejected(self):
        broken = copy.deepcopy(load("spec.json"))
        broken["requirements"][-1]["tests"] = ["test_missing"]
        with self.assertRaisesRegex(ValueError, "unresolved test"):
            validate_spec(load("base_spec.json"), broken, AtlasTests)

    def test_duplicate_link_rejected(self):
        broken = copy.deepcopy(load("spec.json"))
        broken["requirements"][-1]["tests"] = ["test_lab001_create"]
        with self.assertRaisesRegex(ValueError, "duplicate test link"):
            validate_spec(load("base_spec.json"), broken, AtlasTests)


if __name__ == "__main__":
    unittest.main()
```

The negative control succeeds when it detects the defect. For a direct failure demonstration, temporarily replace `Atlas()` with `BaseAtlas()` **only** in `test_req006_preserves_record`. The snapshot equality assertion should fail. Restore the file before capturing the final run.

### 5. Execute and record the local checks

Save `capture.py`:

```python
import hashlib
import json
import sys
import unittest
from pathlib import Path

from atlas import validate_spec
from test_atlas import AtlasTests, load

HERE = Path(__file__).resolve().parent
INPUTS = (
    "base_spec.json", "spec.json", "atlas.py",
    "extend.py", "test_atlas.py", "capture.py"
)


def hashes():
    return {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in INPUTS
    }


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successful_names = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successful_names.append(test._testMethodName)


before = hashes()
base = load("base_spec.json")
spec = load("spec.json")
validate_spec(base, spec, AtlasTests)
linked = {
    name
    for requirement in spec["requirements"]
    for name in requirement["tests"]
}

suite = unittest.defaultTestLoader.loadTestsFromTestCase(AtlasTests)
discovered = [test._testMethodName for test in flatten(suite)]
result = unittest.TextTestRunner(
    verbosity=2, resultclass=RecordingResult
).run(suite)
after = hashes()

successful = result.successful_names
passed = (
    len(discovered) > 0
    and len(discovered) == len(set(discovered))
    and result.testsRun == len(discovered)
    and len(successful) == len(discovered)
    and set(successful) == set(discovered)
    and linked <= set(successful)
    and result.wasSuccessful()
    and not result.skipped
    and not result.expectedFailures
    and not result.unexpectedSuccesses
    and before == after
)
record = {
    "scope": "sequential synthetic Atlas teaching fixture",
    "python": sys.version,
    "command": "python capture.py",
    "input_sha256_before": before,
    "input_sha256_after": after,
    "endpoint_hashes_match": before == after,
    "discovered_tests": discovered,
    "successful_tests": successful,
    "linked_tests": sorted(linked),
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "local_checks_passed": passed,
    "policy_approval": "not assessed; separate authorised decision required",
}
(HERE / "run-record.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
print("Wrote run-record.json")
sys.exit(0 if passed else 1)
```

Run:

```bash
python extend.py
python capture.py
```

The expected local result is exit status zero, ten discovered and successful methods, six linked acceptance methods, no skips and matching endpoint hashes. `run-record.json` records the result and input hashes; the verbose test report appears on the terminal. These are expected outcomes for readers to reproduce, not a claim that this manuscript’s code was independently executed.

The runner derives its linked names from the specification rather than hard-coding a complete test inventory. It nevertheless discovers only `AtlasTests`, and its success rule belongs to this closed fixture. Reviewers must still examine assertions and decide whether the selected cases represent the intended criteria.

### Integrating with the reference lab

To extend the actual v1.1 lab, start with the files in `examples/atlas_ch03/`, record their hashes and run `python -m unittest discover -s examples/atlas_ch03 -p test_atlas.py -v` and `python examples/atlas_ch03/capture.py` from the repository root. Preserve its `REQ-001`–`REQ-005` entries and actual links; add `REQ-006` in a versioned copy using its existing schema and API. Update the identifier and version gates, capture metadata, and positive-and-negative assertions. Run the full suite and the dangling-link check against the modified copy, then retain the new artefacts and execution record.

The present fixture is a deliberately different design, not an automatically compatible patch to the existing Chapter 03 files. A team must compare the interfaces and assertions explicitly before integrating it. In either setting, an authorised reviewer records policy approval separately.
