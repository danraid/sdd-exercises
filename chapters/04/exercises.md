# Chapter 04 | Exercises and knowledge checks

1. **Assumptions and trade-offs.** Explain why the replay contract assumes sequential execution. Describe one concurrent interleaving that a persistent implementation would need to control. Your answer should distinguish a property of the abstract model from a guarantee of a database implementation.

2. **Invariant and failing test.** State an invariant connecting every stored key to an existing record. Write a test that exposes an implementation which deletes a record while retaining its key. Identify whether your test demonstrates a specific violation or proves the invariant universally.

3. **Extend and verify the laboratory.** Add a requirement that a key cannot be reused after its request reaches `decided`: same-kind reuse must now be rejected without changing state. First add a failing acceptance test, then implement the change, increment the specification version and update the validator’s expected version. Run both gates. Your objective checks are: the new test fails before implementation, passes afterwards, and the original lifecycle and authorisation tests still pass. Explain how this changed requirement conflicts with the previous unconditional replay rule and why versioning is necessary.

4. **Evidence review.** Add a test method containing only `pass`, and point one manifest entry to it. Observe that structural resolution can still succeed. Explain what additional review or execution evidence is needed before making any behavioural claim. Does either gate grant policy approval?
