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
