# Chapter 12 | Exercises and knowledge checks

1. **Assumptions and trade-offs.** Explain why literal key comparison is an assumption rather than a consequence of idempotency. Give one advantage and one risk of normalising keys. Your answer should identify a pair of inputs whose treatment would change under your proposed rule.

2. **Invariant and failing test.** Write an invariant stating that a rejected conflicting replay leaves both identity and state unchanged. Add a test that advances a request, attempts a conflicting replay and then checks the original request. Introduce a deliberate mutation that changes the state before raising `ValueError`; verify that your new test detects it.

3. **Laboratory extension.** Implement `REQ-006` using the proposed files, run the tests and record hashes and exit status. Then introduce a dangling link and document the structural failure separately from behavioural results. State who, if anyone, approved the policy. An objective submission includes the changed files, commands, observed output and decision record; it does not claim production security.

4. **Evidence interpretation.** A report says: “All linked tests passed, therefore the release is approved.” Identify at least three missing facts needed to evaluate that claim. Your answer should distinguish artefact identity, behavioural scope and decision authority.
