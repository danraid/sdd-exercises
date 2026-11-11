import copy
import json
from pathlib import Path
import unittest

from atlas import Atlas, validate_spec
from prepare import make_candidate


class AtlasTests(unittest.TestCase):
    def test_req001_accepts_only_declared_request_kinds(self):
        api = Atlas()
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.submit("appointment", "b"), ("R2", "submitted"))
        with self.assertRaises(ValueError):
            api.submit("other", "c")
        with self.assertRaises(ValueError):
            api.submit("permit", "  ")

    def test_req002_replays_and_rejects_conflict(self):
        api = Atlas()
        first = api.submit("permit", "a")
        self.assertEqual(api.submit("permit", "a"), first)
        with self.assertRaises(ValueError):
            api.submit("appointment", "a")
        self.assertEqual(api.submit("permit", "a"), first)
        self.assertEqual(api.submit("appointment", "b"), ("R2", "submitted"))

    def test_req003_enforces_ordered_lifecycle(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")
        self.assertEqual(api.advance("R1", "decided", "reviewer"), "decided")
        with self.assertRaises(ValueError):
            api.advance("R1", "submitted", "reviewer")

    def test_req004_blocks_unauthorised_advancement(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")

    def test_req005_replay_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.advance("R1", "under_review", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "under_review"))
        api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "decided"))

    def test_req006_conflict_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.submit("appointment", "b")
        api.advance("R1", "under_review", "reviewer")
        before = api.snapshot()

        with self.assertRaises(ValueError):
            api.submit("appointment", "a")

        self.assertEqual(api.snapshot(), before)
        self.assertEqual(api.submit("permit", "a"), ("R1", "under_review"))
        self.assertEqual(api.submit("permit", "c"), ("R3", "submitted"))


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent
        self.spec = json.loads((root / "spec.json").read_text(encoding="utf-8"))
        self.base = json.loads(
            (root / "spec-v1.1.json").read_text(encoding="utf-8")
        )
        self.available = set(
            unittest.defaultTestLoader.getTestCaseNames(AtlasTests)
        )

    def test_spec_links_resolve(self):
        validate_spec(self.spec, self.available)

    def test_spec_rejects_dangling_link(self):
        broken = copy.deepcopy(self.spec)
        broken["requirements"][0]["tests"] = ["test_missing"]
        with self.assertRaises(ValueError):
            validate_spec(broken, self.available)

    def test_candidate_preserves_baseline(self):
        self.assertEqual(self.spec, make_candidate(self.base))
        self.assertEqual(
            self.spec["requirements"][:-1], self.base["requirements"]
        )


if __name__ == "__main__":
    unittest.main()
