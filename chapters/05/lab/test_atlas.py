import json
import tempfile
import unittest
from pathlib import Path

from atlas import Atlas, validate_spec


SPEC = Path(__file__).with_name("spec.json")


class ShallowReplayAtlas(Atlas):
    """Deliberately faulty: replay preserves key but resets status."""

    def submit(self, key, payload):
        result = super().submit(key, payload)
        if result["status"] == "withdrawn":
            self._requests[key]["status"] = "active"
            return dict(self._requests[key])
        return result


class AtlasTests(unittest.TestCase):
    def assert_withdrawal_survives_replay(self, service):
        first = service.submit("case-17", "repair request")
        service.withdraw("case-17")
        replay = service.submit("case-17", "repair request")

        # This shallow check alone also passes for the faulty class.
        self.assertEqual(first["key"], replay["key"])
        self.assertEqual(replay["status"], "withdrawn")
        self.assertEqual(service.read("case-17")["status"], "withdrawn")

    def test_req006_replay_preserves_withdrawal(self):
        self.assert_withdrawal_survives_replay(Atlas())

    def test_req006_detects_shallow_replay_bug(self):
        with self.assertRaises(AssertionError):
            self.assert_withdrawal_survives_replay(ShallowReplayAtlas())

    def test_conflict_does_not_restore_request(self):
        service = Atlas()
        service.submit("case-17", "repair request")
        service.withdraw("case-17")
        with self.assertRaises(ValueError):
            service.submit("case-17", "different payload")
        self.assertEqual(service.read("case-17")["status"], "withdrawn")

    def test_spec_links_resolve(self):
        self.assertTrue(validate_spec(SPEC, AtlasTests))

    def test_dangling_link_is_rejected(self):
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        spec["requirements"][0]["tests"].append("test_req006_missing")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_spec(path, AtlasTests)


if __name__ == "__main__":
    unittest.main()
