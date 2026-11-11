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
