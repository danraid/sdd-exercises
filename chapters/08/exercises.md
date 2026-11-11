# Chapter 08 | Exercises and knowledge checks

**1. Assumptions and trade-offs.** Explain why supplying `principal` as a trusted function argument makes the laboratory simpler, and name two claims it prevents the tests from establishing. A satisfactory answer distinguishes key scoping from authentication and identifies at least one deployment concern.

**2. Invariant and failing test.** Write an invariant requiring a successful replay not to allocate a new receipt. Add a test that records both `next_receipt` and `records` before replay and asserts that neither changes afterwards. Introduce a deliberate implementation defect that increments the counter on replay: the new test should fail for that defect and pass after it is corrected.

**3. Structural versus semantic links.** Replace the REQ-006 link in `spec.json` with the existing REQ-002 test name. Does `validate_spec` accept it? Explain why name resolution alone cannot establish that REQ-006 is tested. Restore the correct link afterwards.

**4. Laboratory extension.** Add a local REQ-007 requiring an empty key to be rejected without changing state. Specify the policy explicitly, update the version and expected-ID gates, and implement tests for both a valid key and the prohibited empty key. Check that a dangling test name is rejected, all intended tests pass after implementation, and your record identifies the changed bytes and the still-separate approval decision.
