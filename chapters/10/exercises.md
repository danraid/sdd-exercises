# Chapter 10 | Exercises and knowledge checks

1. **Assumptions and trade-offs.** Explain why a caller-supplied `reviewer` string is inadequate for real authentication. Identify two additional boundaries a deployed service would need to specify. Distinguish the role rule from the mechanism establishing identity.

2. **Invariant and failing test.** In a disposable implementation, make an unauthorised advancement change state before raising `PermissionError`. Write an assertion that exposes the mutation. Explain why an exception-only test would not, by itself, detect it.

3. **Structural versus behavioural evidence.** Replace a linked test body with `pass` in a disposable copy. Explain why name resolution can still succeed and why that does not satisfy the behavioural obligation. Restore the assertion afterwards.

4. **Extend and verify.** Add a second request to the `REQ-006` test and check that rejected advancement of the first changes neither request nor the identifier counter. Run the suite, record the changed file’s digest and state what remains untested. Do not infer policy approval from the run.

5. **Approval decision.** Draft a decision for classroom use, conditional on an actual successful run. State who may approve, which artefacts and evidence are covered, and why the same decision would not authorise deployment.
