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
