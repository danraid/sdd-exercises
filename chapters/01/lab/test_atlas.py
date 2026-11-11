import unittest

from atlas import AtlasService, ContractError


class AtlasAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.service = AtlasService()

    def test_req001_accepts_only_declared_request_kinds(self):
        permit = self.service.submit("permit", "key-1")
        appointment = self.service.submit("appointment", "key-2")
        self.assertEqual(permit.kind, "permit")
        self.assertEqual(appointment.kind, "appointment")
        with self.assertRaises(ContractError):
            self.service.submit("licence", "key-3")

    def test_req002_replays_idempotently(self):
        first = self.service.submit("permit", "  key-1  ")
        replay = self.service.submit("permit", "key-1")
        self.assertEqual(first.request_id, replay.request_id)
        with self.assertRaises(ContractError):
            self.service.submit("permit", "   ")

    def test_req002_rejects_conflicting_replay(self):
        first = self.service.submit("permit", "key-1")
        with self.assertRaises(ContractError):
            self.service.submit("appointment", "key-1")
        self.assertEqual(self.service.get(first.request_id), first)

    def test_req003_enforces_ordered_lifecycle(self):
        first = self.service.submit("permit", "key-1")
        self.assertEqual(first.status, "submitted")
        review = self.service.advance(first.request_id, "reviewer")
        self.assertEqual(review.status, "under_review")
        decided = self.service.advance(first.request_id, "reviewer")
        self.assertEqual(decided.status, "decided")
        with self.assertRaises(ContractError):
            self.service.advance(first.request_id, "reviewer")
        self.assertEqual(self.service.get(first.request_id), decided)

    def test_req004_blocks_unauthorised_advancement(self):
        first = self.service.submit("appointment", "key-1")
        with self.assertRaises(ContractError):
            self.service.advance(first.request_id, "applicant")
        self.assertEqual(self.service.get(first.request_id), first)


if __name__ == "__main__":
    unittest.main()
