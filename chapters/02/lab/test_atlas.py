import unittest
from atlas import Atlas


class AcceptanceTests(unittest.TestCase):
    def test_req001_kinds(self):
        a = Atlas()
        self.assertEqual(a.submit("a", "permit"), "R-0001")
        self.assertEqual(a.submit("b", "appointment"), "R-0002")
        for kind in ("other", "", None):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                a.submit("c", kind)

    def test_req002_replay_and_conflict(self):
        a = Atlas()
        rid = a.submit("a", "permit")
        self.assertEqual(a.submit("a", "permit"), rid)
        with self.assertRaises(ValueError):
            a.submit("a", "appointment")
        self.assertEqual(a.read(rid), ("permit", "submitted"))
        self.assertEqual(a.submit("b", "appointment"), "R-0002")

    def test_req002_blank_keys(self):
        a = Atlas()
        for key in ("", "  ", "\t", None):
            with self.subTest(key=key), self.assertRaises(ValueError):
                a.submit(key, "permit")
        self.assertEqual(a.submit("a", "permit"), "R-0001")

    def test_req003_state_pairs(self):
        states = ("submitted", "under_review", "decided")
        allowed = {
            ("submitted", "under_review"),
            ("under_review", "decided"),
        }
        for source in states:
            for target in states:
                with self.subTest(source=source, target=target):
                    a = Atlas()
                    rid = a.submit("a", "permit")
                    if source in ("under_review", "decided"):
                        a.advance(rid, "reviewer", "under_review")
                    if source == "decided":
                        a.advance(rid, "reviewer", "decided")
                    if (source, target) in allowed:
                        a.advance(rid, "reviewer", target)
                        self.assertEqual(a.read(rid)[1], target)
                    else:
                        with self.assertRaises(ValueError):
                            a.advance(rid, "reviewer", target)
                        self.assertEqual(a.read(rid)[1], source)

    def test_req004_role(self):
        a = Atlas()
        rid = a.submit("a", "permit")
        for role in ("citizen", "", None):
            with self.subTest(role=role), self.assertRaises(PermissionError):
                a.advance(rid, role, "under_review")
            self.assertEqual(a.read(rid)[1], "submitted")
        with self.assertRaises(PermissionError):
            a.advance("missing", "citizen", "under_review")
        with self.assertRaises(KeyError):
            a.advance("missing", "reviewer", "under_review")

    def test_req005_preserves_state(self):
        a = Atlas()
        rid = a.submit("case-A", "permit")
        for state in ("under_review", "decided"):
            a.advance(rid, "reviewer", state)
            self.assertEqual(a.submit("case-A", "permit"), rid)
            self.assertEqual(a.read(rid), ("permit", state))
        self.assertEqual(a.submit("case-B", "appointment"), "R-0002")


if __name__ == "__main__":
    unittest.main()
