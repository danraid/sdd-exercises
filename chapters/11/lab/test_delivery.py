import copy
import json
from pathlib import Path
import unittest


EXPECTED_IDS = {f"REQ-{n:03d}" for n in range(1, 7)}


class Atlas:
    """Synthetic in-memory reconstruction, not the Chapter 03 implementation."""

    def __init__(self):
        self.keys = {}
        self.records = {}

    def submit(self, kind, key):
        if kind not in ("permit", "appointment"):
            raise ValueError("invalid kind")
        if not isinstance(key, str) or not key.strip():
            raise ValueError("blank key")
        if key in self.keys:
            request_id = self.keys[key]
            record = self.records[request_id]
            if record["kind"] != kind:
                raise ValueError("conflicting replay")
            return request_id, record["state"]

        request_id = f"R{len(self.records) + 1}"
        self.keys[key] = request_id
        self.records[request_id] = {
            "kind": kind, "state": "submitted"
        }
        return request_id, "submitted"

    def advance(self, request_id, target, role):
        record = self.records[request_id]
        if role != "reviewer":
            raise PermissionError("reviewer required")
        next_state = {
            "submitted": "under_review",
            "under_review": "decided"
        }.get(record["state"])
        if next_state is None or target != next_state:
            raise ValueError("invalid transition")
        record["state"] = target
        return target


class ResetOnReplayAtlas(Atlas):
    """Deliberate mutant: retains identity but destroys progress."""

    def submit(self, kind, key):
        existed = key in self.keys
        request_id, state = super().submit(kind, key)
        if existed:
            self.records[request_id]["state"] = "submitted"
            state = "submitted"
        return request_id, state


def validate_spec(spec, available):
    """Structural checks only; no claim about test meaning or execution."""
    if spec.get("version") != "1.2-lab-proposal":
        raise ValueError("unexpected version")
    requirements = spec.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")

    ids = []
    for req in requirements:
        if not isinstance(req, dict):
            raise ValueError("invalid requirement")
        req_id = req.get("id")
        invariant = req.get("invariant")
        tests = req.get("tests")
        if not isinstance(req_id, str):
            raise ValueError("invalid identifier")
        if not isinstance(invariant, str) or not invariant.strip():
            raise ValueError("missing invariant")
        if not isinstance(tests, list) or not tests:
            raise ValueError("missing test links")
        if any(not isinstance(name, str) or name not in available
               for name in tests):
            raise ValueError("unresolved test link")
        ids.append(req_id)

    if len(ids) != len(set(ids)) or set(ids) != EXPECTED_IDS:
        raise ValueError("missing, duplicate or unexpected identifier")


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

    def test_req003_enforces_ordered_lifecycle(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")
        self.assertEqual(api.advance("R1", "decided", "reviewer"),
                         "decided")

    def test_req004_blocks_unauthorised_advancement(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))

    def test_req005_replay_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        api.advance("R1", "under_review", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "under_review"))
        api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "decided"))

    def test_req006_rejected_advancement_preserves_state(self):
        api = Atlas()
        api.submit("permit", "a")
        with self.assertRaises(PermissionError):
            api.advance("R1", "under_review", "citizen")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        with self.assertRaises(ValueError):
            api.advance("R1", "decided", "reviewer")
        self.assertEqual(api.submit("permit", "a"), ("R1", "submitted"))
        self.assertEqual(api.advance("R1", "under_review", "reviewer"),
                         "under_review")


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).with_name("spec.json")
        self.spec = json.loads(path.read_text(encoding="utf-8"))
        self.available = set(
            unittest.defaultTestLoader.getTestCaseNames(AtlasTests)
        )

    def test_links_resolve(self):
        validate_spec(self.spec, self.available)

    def test_dangling_link_is_rejected(self):
        broken = copy.deepcopy(self.spec)
        broken["requirements"][0]["tests"] = ["test_missing"]
        with self.assertRaises(ValueError):
            validate_spec(broken, self.available)


class NegativeControlTests(unittest.TestCase):
    def test_identity_only_misses_reset(self):
        api = ResetOnReplayAtlas()
        request_id, _ = api.submit("permit", "mutant")
        api.advance(request_id, "under_review", "reviewer")
        replay_id, replay_state = api.submit("permit", "mutant")

        self.assertEqual(replay_id, request_id)  # Shallow check
        self.assertEqual(replay_state, "submitted")  # Defect observed
        with self.assertRaises(AssertionError):
            self.assertEqual(replay_state, "under_review")


if __name__ == "__main__":
    unittest.main()
