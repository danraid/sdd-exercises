# Chapter 02 | Exercises and knowledge checks

**1. Assumptions and trade-offs.** Explain why `case-A` and ` case-A ` receive different identifiers. Propose a normalisation rule, one risk it introduces and a test that distinguishes it from v1.1. An adequate answer changes the specification as well as the implementation.

**2. Invariant and failing test.** State an invariant that a conflicting replay cannot alter an advanced request. Add a test that advances a `permit`, submits the same key as an `appointment`, expects `ValueError` and checks the original kind and state. Temporarily mutate the conflict branch to change the state before raising; demonstrate that the test fails, then restore it.

**3. Versioned extension.** Create v1.2 with a maximum key length of 32 characters. Write boundary tests for lengths 32 and 33 before changing the handler. Update the validator’s expected specification, implement the rule and produce a new acceptance record. Trace the new requirement to both tests and state whether migration of existing longer keys is in scope.

**4. Evidence interpretation.** A colleague concludes from six passing tests that Atlas is secure for deployment. Identify three unsupported parts of the conclusion. Your answer should distinguish role strings from authentication, an in-memory object from a networked service, and sequential tests from concurrency evidence.
