# Chapter 11 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

### Status and objective

This is an **author-created design exercise**, not a claim that a Chapter 11 fixture has already been integrated into the repository or that the following proposed tests have been run. The canonical Chapter 03 implementation and tests do exist in the repository; the new Chapter 11 files are an independent reconstruction, not a verified migration of those artefacts.

To undertake the exercise, create the two proposed files in a new local directory. The prototype reconstructs a small, stand-alone in-memory Atlas and retains the Chapter 03 requirement IDs and test names for teaching purposes. It proposes a new REQ-006: **an unauthorised or invalid advancement of an existing request leaves its state unchanged**. The proposed label `1.2-lab-proposal` is not an established Atlas version.

The role string is a teaching placeholder, not authentication. The prototype has no network, storage or concurrency model.

### Proposed file: `spec.json`

```json
{
  "version": "1.2-lab-proposal",
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
      "invariant": "Rejected advancement of an existing request preserves state.",
      "tests": ["test_req006_rejected_advancement_preserves_state"]
    }
  ]
}
```

### Proposed file: `test_delivery.py`

```python
import copy
import json
from pathlib import Path
import unittest


EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 7)}


class Atlas:
    """Synthetic in-memory reconstruction, not the Chapter 03 implementation."""

    def __init__(self):
        self.keys = {}
        self.records = {}

    def submit(self, kind, key):
        if kind not in ("permit", "appointment"):
            raise ValueError("invalid kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("blank key")
        if key in self.keys:
            request_id = self.keys[key]
            record = self.records[request_id]
            if record["kind"] != kind:
                raise ValueError("conflicting replay")
            return request_id, record["state"]

        request_id = f"R{len(self.records) + 1}"
        self.keys[key] = request_id
        self.records[request_id] = {
            "kind": kind, "state": "submitted"
        }
        return request_id, "submitted"

    def advance(self, request_id, target, role):
        record = self.records[request_id]
        if role != "reviewer":
            raise PermissionError("reviewer required")
        next_state = {
            "submitted": "under_review",
            "under_review": "decided"
        }.get(record["state"])
        if next_state is None or target != next_state:
            raise ValueError("invalid transition")
        record["state"] = target
        return target


class ResetOnReplayAtlas(Atlas):
    """Deliberate mutant: retains identity but destroys progress."""

    def submit(self, kind, key):
        existed = key in self.keys
        request_id, state = super().submit(kind, key)
        if existed:
            self.records[request_id]["state"] = "submitted"
            state = "submitted"
        return request_id, state


def validate_spec(spec, available):
    """Structural checks only; no claim about test meaning or execution."""
    if spec.get("version") != "1.2-lab-proposal":
        raise ValueError("unexpected version")
    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = []
    for req in requirements:
        if not isinstance(req, dict):
            raise ValueError("invalid requirement")
        req_id = req.get("id")
        invariant = req.get("invariant")
        tests = req.get("tests")
        if not isinstance(req_id, str):
            raise ValueError("invalid identifier")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if not isinstance(tests, list) or not tests:
            raise ValueError("missing test links")
        if any(not isinstance(name, str) or name not in available
               for name in tests):
            raise ValueError("unresolved test link")
        ids.append(req_id)

    if len(ids) != len(set(ids)) or set(ids) != EXPECTED_IDS:
        raise ValueError("missing, duplicate or unexpected identifier")


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

    def test_req003_enforces_ordered_lifecycle(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")
        self.assertEqual(api.advance("R1", "decided", "reviewer"),
                         "decided")

    def test_req004_blocks_unauthorised_advancement(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))

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
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("spec.json")
        self.spec = json.loads(path.read_text(encoding="utf-8"))
        self.available = set(
            unittest.defaultTestLoader.getTestCaseNames(AtlasTests)
        )

    def test_links_resolve(self):
        validate_spec(self.spec, self.available)

    def test_dangling_link_is_rejected(self):
        broken = copy.deepcopy(self.spec)
        broken["requirements"][0]["tests"] = ["test_missing"]
        with self.assertRaises(ValueError):
            validate_spec(broken, self.available)


class NegativeControlTests(unittest.TestCase):
    def test_identity_only_misses_reset(self):
        api = ResetOnReplayAtlas()
        request_id, _ = api.submit("permit", "mutant")
        api.advance(request_id, "under_review", "reviewer")
        replay_id, replay_state = api.submit("permit", "mutant")

        self.assertEqual(replay_id, request_id)  # Shallow check
        self.assertEqual(replay_state, "submitted")  # Defect observed
        with self.assertRaises(AssertionError):
            self.assertEqual(replay_state, "under_review")


if __name__ == "__main__":
    unittest.main()
```

### Execution and interpretation

After creating the files locally, run the following from their directory. Record the complete output and exit status rather than treating the command itself as evidence of success.

```bash
python --version
python -m unittest -v test_delivery
```

Record SHA-256 digests of both input files and retain them with the command, tool version and output. For example:

```bash
python -c "import hashlib; from pathlib import Path; \
[(print(p, hashlib.sha256(Path(p).read_bytes()).hexdigest())) \
for p in ('spec.json', 'test_delivery.py')]"
```

For a CI adaptation, use an immutable checkout and retain its commit identifier as well. If files can change while tests run, pre-run hashes alone do not establish what was executed; protect the workspace or verify the inputs again. This exercise produces no deployment artefact, so an artefact digest and release approval would have to be added by a real delivery process.

The objective check is that the test command exits successfully after the files are created as specified. The dangling-link test should establish only that this validator rejects that particular missing name. The negative control is designed to show the identity check succeeding on the mutant while state preservation fails. Neither result, if obtained, approves policy or proves behaviour beyond the exercised cases.

For a further check, replace the REQ-006 test link in `spec.json` with `test_missing` and rerun the suite. The structural test should fail; restore the link and rerun. Then remove the state assertions from `test_req006_rejected_advancement_preserves_state` and explain why name resolution alone cannot detect the weakened test. Do not record either expected outcome as an observation without running it.
