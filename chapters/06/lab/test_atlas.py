import copy
import json
import unittest
from pathlib import Path

from atlas import Atlas, BaseAtlas, validate_spec

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class AtlasTests(unittest.TestCase):
    def test_lab001_create(self):
        self.assertEqual("A-1", Atlas().submit("k-17", "repair"))

    def test_lab002_replay_and_conflict(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        self.assertEqual(first, service.submit("k-17", "repair"))
        before = service.snapshot("k-17")
        with self.assertRaises(ValueError):
            service.submit("k-17", "housing")
        self.assertEqual(before, service.snapshot("k-17"))

    def test_lab003_snapshot(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        record = service.snapshot("k-17")
        self.assertEqual(first, record["id"])
        self.assertEqual("repair", record["payload"])

    def test_lab004_review(self):
        service = Atlas()
        service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        self.assertTrue(service.snapshot("k-17")["reviewed"])

    def test_lab005_distinct_ids(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        second = service.submit("k-18", "housing")
        self.assertNotEqual(first, second)

    def test_req006_preserves_record(self):
        service = Atlas()
        first = service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        before = service.snapshot("k-17")
        self.assertEqual(first, service.submit("k-17", "repair"))
        self.assertEqual(before, service.snapshot("k-17"))
        with self.assertRaises(ValueError):
            service.submit("k-17", "housing")
        self.assertEqual(before, service.snapshot("k-17"))

    def test_shallow_check_misses_defect(self):
        service = BaseAtlas()
        first = service.submit("k-17", "repair")
        service.mark_reviewed("k-17")
        before = service.snapshot("k-17")
        self.assertEqual(first, service.submit("k-17", "repair"))
        self.assertNotEqual(before, service.snapshot("k-17"))
        self.assertFalse(service.snapshot("k-17")["reviewed"])

    def test_spec_links_resolve(self):
        validate_spec(load("base_spec.json"), load("spec.json"), AtlasTests)

    def test_dangling_link_rejected(self):
        broken = copy.deepcopy(load("spec.json"))
        broken["requirements"][-1]["tests"] = ["test_missing"]
        with self.assertRaisesRegex(ValueError, "unresolved test"):
            validate_spec(load("base_spec.json"), broken, AtlasTests)

    def test_duplicate_link_rejected(self):
        broken = copy.deepcopy(load("spec.json"))
        broken["requirements"][-1]["tests"] = ["test_lab001_create"]
        with self.assertRaisesRegex(ValueError, "duplicate test link"):
            validate_spec(load("base_spec.json"), broken, AtlasTests)


if __name__ == "__main__":
    unittest.main()
