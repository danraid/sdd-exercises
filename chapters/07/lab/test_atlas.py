import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from atlas import Atlas, validate_migration, validate_spec, with_description


ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class TestAtlas(unittest.TestCase):
    def setUp(self):
        self.api = Atlas()

    def test_req001_kind(self):
        with self.assertRaises(ValueError):
            self.api.submit("A-1", "unsupported")
        self.assertEqual(self.api.records, {})

    def test_req002_replay_preserves_record(self):
        first = self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        replay = self.api.submit("A-1", "maintenance")
        self.assertEqual(replay, first)
        self.assertEqual(self.api.records, before)

    def test_req002_conflict_rejected(self):
        self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        with self.assertRaises(ValueError):
            self.api.submit("A-1", "other")
        self.assertEqual(self.api.records, before)

    # Preserve the two v1.0 link names as aliases to the same test bodies.
    test_req002_replay = test_req002_replay_preserves_record
    test_req002_conflict = test_req002_conflict_rejected

    def test_req003_transition(self):
        self.api.submit("A-1", "maintenance")
        result = self.api.review("A-1", reviewer=True)
        self.assertEqual(result["status"], "reviewed")

    def test_req004_reviewer(self):
        self.api.submit("A-1", "maintenance")
        before = deepcopy(self.api.records)
        with self.assertRaises(PermissionError):
            self.api.review("A-1", reviewer=False)
        self.assertEqual(self.api.records, before)

    def test_req005_description_boundary(self):
        with patch.object(self.api, "submit", wraps=self.api.submit) as submit:
            guarded = with_description(submit)
            result = guarded("Repair a bench", "A-1", kind="maintenance")
            self.assertEqual(result["status"], "submitted")
            submit.assert_called_once_with("A-1", kind="maintenance")

            before = deepcopy(self.api.records)
            submit.reset_mock()
            for invalid in ("", "   ", "\t", None, 42):
                with self.subTest(description=invalid):
                    with self.assertRaises(ValueError):
                        guarded(invalid, "A-2", kind="maintenance")
                    submit.assert_not_called()
                    self.assertEqual(self.api.records, before)


class TestSpecification(unittest.TestCase):
    def test_versions_and_migration(self):
        baseline, proposed = load("baseline.json"), load("spec.json")
        validate_spec(
            baseline, "1.0",
            {"REQ-001", "REQ-002", "REQ-003", "REQ-004"},
            TestAtlas,
        )
        validate_spec(
            proposed, "1.1",
            {"REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"},
            TestAtlas,
        )
        validate_migration(baseline, proposed)

    def test_dangling_link_is_rejected(self):
        proposed = load("spec.json")
        proposed["requirements"][-1]["tests"] = ["test_missing"]
        with self.assertRaisesRegex(ValueError, "unresolved test link"):
            validate_spec(
                proposed, "1.1",
                {"REQ-001", "REQ-002", "REQ-003", "REQ-004", "REQ-005"},
                TestAtlas,
            )


if __name__ == "__main__":
    unittest.main()
