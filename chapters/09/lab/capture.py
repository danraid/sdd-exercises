import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
INPUTS = [
    "spec-v1.1.json", "spec.json", "prepare.py",
    "atlas.py", "test_atlas.py", "capture.py",
]


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in INPUTS
    }


if __name__ == "__main__":
    before = hashes()
    command = [sys.executable, "-m", "unittest", "-v", "test_atlas"]
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    after = hashes()
    record = {
        "scope": "Reconstructed sequential Atlas model and candidate REQ-006",
        "python": sys.version,
        "command": command,
        "input_sha256_before": before,
        "input_sha256_after": after,
        "inputs_unchanged": before == after,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "policy_approval": "not recorded",
    }
    (ROOT / "run-record.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    sys.exit(0 if result.returncode == 0 and before == after else 1)
