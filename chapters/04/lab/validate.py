import ast
import json
import sys
from pathlib import Path


def validate():
    spec = json.loads(Path("spec.json").read_text(encoding="utf-8"))
    if spec.get("version") != "1.1":
        raise ValueError("expected Atlas specification version 1.1")

    requirements = spec.get("requirements")
    expected = {"REQ-001", "REQ-002", "REQ-003", "REQ-004"}
    if not isinstance(requirements, dict) or set(requirements) != expected:
        raise ValueError("missing or unexpected requirement identifiers")

    tree = ast.parse(Path("test_atlas.py").read_text(encoding="utf-8"))
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == spec.get("test_class")
    ]
    if len(classes) != 1:
        raise ValueError("expected exactly one named test class")

    methods = [
        node.name for node in classes[0].body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) != len(set(methods)):
        raise ValueError("duplicate test method name")

    for req, names in requirements.items():
        if not isinstance(names, list) or not names:
            raise ValueError(f"{req}: expected a non-empty test list")
        if any(not isinstance(name, str) or not name.startswith("test_")
               for name in names):
            raise ValueError(f"{req}: invalid test name")
        if len(names) != len(set(names)):
            raise ValueError(f"{req}: duplicate test reference")
        missing = set(names) - set(methods)
        if missing:
            raise ValueError(f"{req}: unresolved names {sorted(missing)}")

    print("STRUCTURAL PASS: declared test names resolve; tests not run.")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        print(f"STRUCTURAL FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
