import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NEW_REQUIREMENT = {
    "id": "REQ-006",
    "invariant": (
        "A conflicting key reuse leaves records, key bindings and "
        "the next request identifier unchanged."
    ),
    "tests": ["test_req006_conflict_preserves_state"],
}


def make_candidate(base):
    if base.get("version") != "1.1":
        raise ValueError("expected the supplied v1.1 specification")
    requirements = base.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
    if any(item.get("id") == "REQ-006" for item in requirements):
        raise ValueError("REQ-006 already exists")

    candidate = copy.deepcopy(base)
    candidate["version"] = "1.2"
    candidate["requirements"].append(copy.deepcopy(NEW_REQUIREMENT))
    return candidate


if __name__ == "__main__":
    base = json.loads((ROOT / "spec-v1.1.json").read_text(encoding="utf-8"))
    candidate = make_candidate(base)
    (ROOT / "spec.json").write_text(
        json.dumps(candidate, indent=2) + "\n", encoding="utf-8"
    )
