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
