# Chapter 02 | Complete practical laboratory

Original code listings and running instructions from the textbook, retained in full for reproducibility. The individual source files are also supplied in `lab/`. All results described as expected must be verified locally before they are reported as observed.

This independent laboratory extends the Chapter 1 behaviour using synthetic data. It requires Python 3.10 or later and the standard library. Create an empty directory and save the following four files in it.

The specification is deliberately small. Its fixed lines are machine-checkable identifiers for this exercise; they do not replace human review of the policy.

### Specification

Save as `SPEC.md`:

```text
Atlas specification v1.1
Scope: sequential, in-memory; no network or authentication.
REQ-001: kinds are permit and appointment.
REQ-002: matching key and kind return the original ID; conflict fails.
REQ-003: submitted -> under_review -> decided; no other transitions.
REQ-004: only the reviewer role string may advance.
REQ-005: matching replay preserves lifecycle state.
Local: non-blank keys compare exactly; IDs are allocated sequentially.
```

Thus `case-A` and ` case-A ` are different keys. Invalid keys, kinds, conflicts and transitions raise `ValueError`; an unauthorised advance raises `PermissionError`. An authorised advance of an unknown identifier raises `KeyError`. These exception choices are local interface decisions for the exercise.

### Handler

Save as `atlas.py`:

```python
class Atlas:
    def __init__(self):
        self._by_key = {}  # key -> (kind, ID)
        self._by_id = {}   # ID -> (kind, state)
        self._next_id = 1

    def submit(self, key, kind):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("non-blank string key required")
        if kind not in ("permit", "appointment"):
            raise ValueError("unsupported kind")
        if key in self._by_key:
            old_kind, request_id = self._by_key[key]
            if kind != old_kind:
                raise ValueError("conflicting replay")
            return request_id

        request_id = f"R-{self._next_id:04d}"
        self._next_id += 1
        self._by_key[key] = (kind, request_id)
        self._by_id[request_id] = (kind, "submitted")
        return request_id

    def read(self, request_id):
        return self._by_id[request_id]

    def advance(self, request_id, role, target):
        if role != "reviewer":
            raise PermissionError("reviewer required")
        kind, state = self._by_id[request_id]
        allowed = {
            "submitted": "under_review",
            "under_review": "decided",
        }
        if state not in allowed or target != allowed[state]:
            raise ValueError("invalid transition")
        self._by_id[request_id] = (kind, target)
```

### Acceptance tests

Save as `test_atlas.py`:

```python
import unittest
from atlas import Atlas


class AcceptanceTests(unittest.TestCase):
    def test_req001_kinds(self):
        a = Atlas()
        self.assertEqual(a.submit("a", "permit"), "R-0001")
        self.assertEqual(a.submit("b", "appointment"), "R-0002")
        for kind in ("other", "", None):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                a.submit("c", kind)

    def test_req002_replay_and_conflict(self):
        a = Atlas()
        rid = a.submit("a", "permit")
        self.assertEqual(a.submit("a", "permit"), rid)
        with self.assertRaises(ValueError):
            a.submit("a", "appointment")
        self.assertEqual(a.read(rid), ("permit", "submitted"))
        self.assertEqual(a.submit("b", "appointment"), "R-0002")

    def test_req002_blank_keys(self):
        a = Atlas()
        for key in ("", "  ", "\t", None):
            with self.subTest(key=key), self.assertRaises(ValueError):
                a.submit(key, "permit")
        self.assertEqual(a.submit("a", "permit"), "R-0001")

    def test_req003_state_pairs(self):
        states = ("submitted", "under_review", "decided")
        allowed = {
            ("submitted", "under_review"),
            ("under_review", "decided"),
        }
        for source in states:
            for target in states:
                with self.subTest(source=source, target=target):
                    a = Atlas()
                    rid = a.submit("a", "permit")
                    if source in ("under_review", "decided"):
                        a.advance(rid, "reviewer", "under_review")
                    if source == "decided":
                        a.advance(rid, "reviewer", "decided")
                    if (source, target) in allowed:
                        a.advance(rid, "reviewer", target)
                        self.assertEqual(a.read(rid)[1], target)
                    else:
                        with self.assertRaises(ValueError):
                            a.advance(rid, "reviewer", target)
                        self.assertEqual(a.read(rid)[1], source)

    def test_req004_role(self):
        a = Atlas()
        rid = a.submit("a", "permit")
        for role in ("citizen", "", None):
            with self.subTest(role=role), self.assertRaises(PermissionError):
                a.advance(rid, role, "under_review")
            self.assertEqual(a.read(rid)[1], "submitted")
        with self.assertRaises(PermissionError):
            a.advance("missing", "citizen", "under_review")
        with self.assertRaises(KeyError):
            a.advance("missing", "reviewer", "under_review")

    def test_req005_preserves_state(self):
        a = Atlas()
        rid = a.submit("case-A", "permit")
        for state in ("under_review", "decided"):
            a.advance(rid, "reviewer", state)
            self.assertEqual(a.submit("case-A", "permit"), rid)
            self.assertEqual(a.read(rid), ("permit", state))
        self.assertEqual(a.submit("case-B", "appointment"), "R-0002")


if __name__ == "__main__":
    unittest.main()
```

The state-pair test covers all nine pairs of the three named states. It does not cover every possible invalid target or sequence. The replay test observes both advanced states; it does not exhaust all key strings.

### Specification validator and acceptance record

Save as `validate.py`:

```python
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
FILES = ("SPEC.md", "atlas.py", "test_atlas.py", "validate.py")
EXPECTED = [
    "Atlas specification v1.1",
    "Scope: sequential, in-memory; no network or authentication.",
    "REQ-001: kinds are permit and appointment.",
    "REQ-002: matching key and kind return the original ID; conflict fails.",
    "REQ-003: submitted -> under_review -> decided; no other transitions.",
    "REQ-004: only the reviewer role string may advance.",
    "REQ-005: matching replay preserves lifecycle state.",
    "Local: non-blank keys compare exactly; IDs are allocated sequentially.",
]


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in FILES
    }


before = hashes()
spec_ok = (ROOT / "SPEC.md").read_text(encoding="utf-8").splitlines() == EXPECTED
command = [sys.executable, "-m", "unittest", "-v", "test_atlas"]
run = subprocess.run(
    command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT, check=False,
)
after = hashes()
unchanged = before == after
accepted = spec_ok and run.returncode == 0 and unchanged

print("Atlas v1.1 acceptance record")
print("Python:", sys.version.replace("\n", " "))
print("Validation command: python validate.py")
print("Test command:", " ".join(command))
for name, digest in before.items():
    print(f"SHA-256 {name}: {digest}")
print("Specification format:", "PASS" if spec_ok else "FAIL")
print("Files unchanged during run:", "PASS" if unchanged else "FAIL")
print("Test output:")
print(run.stdout, end="")
print("Test exit code:", run.returncode)
print("Decision:", "SCOPED ACCEPT" if accepted else "BLOCK")
sys.exit(0 if accepted else 1)
```

The validator checks the exact expected specification lines, runs the tests, records SHA-256 content identifiers and checks that the four files did not change during the run. It is intentionally a *format and evidence validator*: it cannot decide whether the requirement is socially appropriate, nor whether the tests fully implement its meaning.

From the directory containing the files, run:

```bash
python validate.py > acceptance.txt
cat acceptance.txt
```

On Windows, use `type acceptance.txt` for the second command. A successful record contains six passing tests, `OK`, test exit code `0` and `Decision: SCOPED ACCEPT`. The generated record supplies the actual Python environment, test command and four immutable content identifiers for that run. Preserve it with the four files; independently recomputing their hashes can verify that the retained contents match the record.

**Sample record interpretation.** A completed local record has this structure; the hash values and Python version must come from the run rather than be copied from an illustration:

```text
Atlas v1.1 acceptance record
Python: <actual interpreter version>
Validation command: python validate.py
Test command: <actual interpreter> -m unittest -v test_atlas
SHA-256 SPEC.md: <actual 64-hex-digit content identifier>
SHA-256 atlas.py: <actual 64-hex-digit content identifier>
SHA-256 test_atlas.py: <actual 64-hex-digit content identifier>
SHA-256 validate.py: <actual 64-hex-digit content identifier>
Specification format: PASS
Files unchanged during run: PASS
Test output:
<individual test results, followed by OK>
Test exit code: 0
Decision: SCOPED ACCEPT
```

This is an expected record format, not a claim that a run has already occurred. The reproducible acceptance record is the populated `acceptance.txt` produced locally. Its decision means that this validator accepted these contents for the stated synthetic boundary; it is not an independent approval or a production release decision.

To check that the new test can detect the motivating fault, temporarily replace the matching-replay branch with the counterexample in the worked example. Run the validator again: `test_req005_preserves_state` should fail and the decision should be `BLOCK`. Restore the handler, rerun validation and retain the new passing record. The two records will identify different implementation contents by hash.
