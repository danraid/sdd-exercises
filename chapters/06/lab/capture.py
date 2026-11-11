import hashlib
import json
import sys
import unittest
from pathlib import Path

from atlas import validate_spec
from test_atlas import AtlasTests, load

HERE = Path(__file__).resolve().parent
INPUTS = (
    "base_spec.json", "spec.json", "atlas.py",
    "extend.py", "test_atlas.py", "capture.py"
)


def hashes():
    return {
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in INPUTS
    }


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successful_names = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successful_names.append(test._testMethodName)


before = hashes()
base = load("base_spec.json")
spec = load("spec.json")
validate_spec(base, spec, AtlasTests)
linked = {
    name
    for requirement in spec["requirements"]
    for name in requirement["tests"]
}

suite = unittest.defaultTestLoader.loadTestsFromTestCase(AtlasTests)
discovered = [test._testMethodName for test in flatten(suite)]
result = unittest.TextTestRunner(
    verbosity=2, resultclass=RecordingResult
).run(suite)
after = hashes()

successful = result.successful_names
passed = (
    len(discovered) > 0
    and len(discovered) == len(set(discovered))
    and result.testsRun == len(discovered)
    and len(successful) == len(discovered)
    and set(successful) == set(discovered)
    and linked <= set(successful)
    and result.wasSuccessful()
    and not result.skipped
    and not result.expectedFailures
    and not result.unexpectedSuccesses
    and before == after
)
record = {
    "scope": "sequential synthetic Atlas teaching fixture",
    "python": sys.version,
    "command": "python capture.py",
    "input_sha256_before": before,
    "input_sha256_after": after,
    "endpoint_hashes_match": before == after,
    "discovered_tests": discovered,
    "successful_tests": successful,
    "linked_tests": sorted(linked),
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "local_checks_passed": passed,
    "policy_approval": "not assessed; separate authorised decision required",
}
(HERE / "run-record.json").write_text(
    json.dumps(record, indent=2) + "\n", encoding="utf-8"
)
print("Wrote run-record.json")
sys.exit(0 if passed else 1)
