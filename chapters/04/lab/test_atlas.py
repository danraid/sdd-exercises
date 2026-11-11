import unittest
from dataclasses import replace

from atlas import Atlas


class ResetOnReplayAtlas(Atlas):
    """Intentional mutant for the negative control only."""

    def submit(self, key, kind):
        existed = key in self._keys
        request_id = super().submit(key, kind)
        if existed:
            self._records[request_id] = replace(
                self._records[request_id], state="submitted"
            )
        return request_id


class TestAtlasAcceptance(unittest.TestCase):
    def test_req001_declared_kinds(self):
        api = Atlas()
        self.assertEqual(api.get(api.submit("a", "permit")).kind, "permit")
        self.assertEqual(
            api.get(api.submit("b", "appointment")).kind, "appointment"
        )
        with self.assertRaises(ValueError):
            api.submit("c", "licence")
        with self.assertRaises(ValueError):
            api.submit("   ", "permit")

    def test_req002_replay_preserves_progress(self):
        api = Atlas()
        request_id = api.submit("key-1", "permit")
        api.advance(request_id, "under_review", "reviewer")
        before = api.get(request_id)

        replay_id = api.submit("key-1", "permit")

        self.assertEqual(replay_id, request_id)
        self.assertEqual(api.get(request_id), before)

    def test_req002_conflicting_replay_rejected(self):
        api = Atlas()
        request_id = api.submit("key-2", "permit")
        before = api.get(request_id)
        with self.assertRaises(ValueError):
            api.submit("key-2", "appointment")
        self.assertEqual(api.get(request_id), before)
        self.assertEqual(api.submit("key-2", "permit"), request_id)

    def test_req003_ordered_lifecycle(self):
        api = Atlas()
        request_id = api.submit("key-3", "permit")
        with self.assertRaises(ValueError):
            api.advance(request_id, "decided", "reviewer")
        self.assertEqual(api.get(request_id).state, "submitted")

        api.advance(request_id, "under_review", "reviewer")
        api.advance(request_id, "decided", "reviewer")
        self.assertEqual(api.get(request_id).state, "decided")
        with self.assertRaises(ValueError):
            api.advance(request_id, "submitted", "reviewer")
        self.assertEqual(api.get(request_id).state, "decided")

    def test_req004_reviewer_only(self):
        api = Atlas()
        request_id = api.submit("key-4", "appointment")
        with self.assertRaises(PermissionError):
            api.advance(request_id, "under_review", "resident")
        self.assertEqual(api.get(request_id).state, "submitted")


class TestNegativeControl(unittest.TestCase):
    def test_identity_only_misses_reset(self):
        api = ResetOnReplayAtlas()
        request_id = api.submit("mutant-key", "permit")
        api.advance(request_id, "under_review", "reviewer")

        replay_id = api.submit("mutant-key", "permit")

        self.assertEqual(replay_id, request_id)  # Shallow check passes.
        self.assertEqual(api.get(request_id).state, "submitted")
        # The second assertion demonstrates the defect; it is not approval.


if __name__ == "__main__":
    unittest.main()
