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
