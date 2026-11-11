# Chapter 05 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This standalone laboratory is an **overlay** on the Atlas storyline. It does not replace the earlier files or claim to reproduce their suite. Use a new directory so that existing artefacts remain intact. Python 3.9 or later and the standard library are sufficient.

### 1. Create the specification

Create `atlas_ch05/spec.json`:

```json
{
  "version": "atlas-overlay-1.2",
  "requirements": [
    {
      "id": "REQ-006",
      "name": "withdrawal remains terminal",
      "invariant": "Replay of the original submission preserves withdrawn state.",
      "tests": [
        "test_req006_replay_preserves_withdrawal",
        "test_req006_detects_shallow_replay_bug"
      ]
    }
  ]
}
```

This is a small structured specification, not a complete formal schema. The tests interpret its English invariant; the validator does not prove equivalence between text and tests.

### 2. Implement the model and structural validator

Create `atlas_ch05/atlas.py`:

```python
import json
from pathlib import Path


class Atlas:
    """Synthetic, single-process request store."""

    def __init__(self):
        self._requests = {}

    def submit(self, key, payload):
        if key in self._requests:
            record = self._requests[key]
            if record["payload"] != payload:
                raise ValueError("idempotency-key conflict")
            return dict(record)

        record = {"key": key, "payload": payload, "status": "active"}
        self._requests[key] = record
        return dict(record)

    def withdraw(self, key):
        self._requests[key]["status"] = "withdrawn"
        return dict(self._requests[key])

    def read(self, key):
        return dict(self._requests[key])


def validate_spec(path, test_class):
    """Resolve this overlay's required fields and test method names."""
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    if spec.get("version") != "atlas-overlay-1.2":
        raise ValueError("unexpected overlay version")

    requirements = spec.get("requirements")
    if not isinstance(requirements, list) or len(requirements) != 1:
        raise ValueError("expected exactly one overlay requirement")

    req = requirements[0]
    if not isinstance(req, dict) or req.get("id") != "REQ-006":
        raise ValueError("expected REQ-006")

    invariant = req.get("invariant")
    if not isinstance(invariant, str) or not invariant.strip():
        raise ValueError("invariant must be non-empty")

    links = req.get("tests")
    if not isinstance(links, list) or not links:
        raise ValueError("tests must be a non-empty list")
    for name in links:
        if (
            not isinstance(name, str)
            or not name.startswith("test_req006_")
            or not callable(getattr(test_class, name, None))
        ):
            raise ValueError(f"unresolved test: {name!r}")
    return True
```

The returned dictionaries are shallow copies. With the string payload used here, callers cannot modify the stored fields through a returned dictionary. Mutable nested payloads would require additional treatment. The class is not designed for concurrent or persistent use.

### 3. Add behavioural and structural tests

Create `atlas_ch05/test_atlas.py`:

```python
import json
import tempfile
import unittest
from pathlib import Path

from atlas import Atlas, validate_spec


SPEC = Path(__file__).with_name("spec.json")


class ShallowReplayAtlas(Atlas):
    """Deliberately faulty: replay preserves key but resets status."""

    def submit(self, key, payload):
        result = super().submit(key, payload)
        if result["status"] == "withdrawn":
            self._requests[key]["status"] = "active"
            return dict(self._requests[key])
        return result


class AtlasTests(unittest.TestCase):
    def assert_withdrawal_survives_replay(self, service):
        first = service.submit("case-17", "repair request")
        service.withdraw("case-17")
        replay = service.submit("case-17", "repair request")

        # This shallow check alone also passes for the faulty class.
        self.assertEqual(first["key"], replay["key"])
        self.assertEqual(replay["status"], "withdrawn")
        self.assertEqual(service.read("case-17")["status"], "withdrawn")

    def test_req006_replay_preserves_withdrawal(self):
        self.assert_withdrawal_survives_replay(Atlas())

    def test_req006_detects_shallow_replay_bug(self):
        with self.assertRaises(AssertionError):
            self.assert_withdrawal_survives_replay(ShallowReplayAtlas())

    def test_conflict_does_not_restore_request(self):
        service = Atlas()
        service.submit("case-17", "repair request")
        service.withdraw("case-17")
        with self.assertRaises(ValueError):
            service.submit("case-17", "different payload")
        self.assertEqual(service.read("case-17")["status"], "withdrawn")

    def test_spec_links_resolve(self):
        self.assertTrue(validate_spec(SPEC, AtlasTests))

    def test_dangling_link_is_rejected(self):
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        spec["requirements"][0]["tests"].append("test_req006_missing")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_spec(path, AtlasTests)


if __name__ == "__main__":
    unittest.main()
```

The negative test is expected to **pass** because it checks that the oracle detects the deliberately faulty class. The conflict test adds an adjacent case; it is not a substitute for the earlier `REQ-002` suite.

### 4. Capture a reproducible run

Create `atlas_ch05/capture.py`:

```python
import hashlib
import platform
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUTS = ("spec.json", "atlas.py", "test_atlas.py", "capture.py")
command = [sys.executable, "-m", "unittest", "test_atlas", "-v"]

result = subprocess.run(
    command, cwd=HERE, text=True, capture_output=True
)

lines = [
    "Scope: synthetic Atlas REQ-006 overlay; not complete v1.2",
    f"Python: {sys.version}",
    f"Platform: {platform.platform()}",
    f"Command: {command!r}",
    f"Working directory: {HERE}",
]
for name in INPUTS:
    digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
    lines.append(f"SHA-256 {name}: {digest}")

lines.extend([
    f"Exit status: {result.returncode}",
    "--- stdout ---",
    result.stdout,
    "--- stderr ---",
    result.stderr,
    "Policy approval: NOT RECORDED",
])
record = "\n".join(lines) + "\n"
(HERE / "run-record.txt").write_text(record, encoding="utf-8")
print(record)
sys.exit(result.returncode)
```

From the parent directory, run:

```bash
python atlas_ch05/capture.py
```

The objective check is exit status zero and **five tests** reported as passing, including the dangling-link and faulty-implementation checks. The Python version, paths and digests depend on the local environment. Inspect `run-record.txt`; do not treat an expected result as a completed local run.

The record is not a tamper-proof attestation. It hashes files after execution and does not independently prove that they were unchanged while tests ran. Stronger provenance would use controlled execution against immutable inputs and retain the record separately.

### 5. Plan integration without inventing history

For a complete proposed Atlas v1.2, integrate the operation and requirement into the actual earlier artefacts rather than substituting this overlay. First inspect their `REQ-002` links and test methods. Resolve the discrepancy between the two separate names and the reference note’s claimed combined name; record the observed old links and any new links. Do not delete or rename a link on the strength of the note alone.

Preserve the existing requirements, update the actual `EXPECTED_IDS`, version gate and capture-script version, and add the new tests. Run the existing suite and a deliberate dangling-link check. Record input hashes and the separate authorised policy decision. Until then, a passing overlay run is evidence only for its stated cases.
