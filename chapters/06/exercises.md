# Chapter 06 | Exercises and knowledge checks

**1. Explain assumptions and trade-offs.** Why does returning the existing record suffice for the sequential example, yet not establish correctness for a concurrent persistent service? A satisfactory answer distinguishes state preservation from atomicity and recovery.

**2. Write an invariant and a failing test.** Add a `priority` field and an operation that changes it. Specify whether replay may change priority. Demonstrate a failing snapshot test against a faulty implementation that resets it, and explain why an identifier-only assertion misses the defect.

**3. Implement and verify an extension.** Add `REQ-007` and a linked test for priority preservation. Update the derivation and validator deliberately, demonstrate rejection of a dangling link, then capture a passing run. Submit the changed files and record; identify policy approval as separate.

**4. Audit migration evidence.** List the source and destination specifications, test implementations, hashes and revision evidence needed to assess the reference lab’s `REQ-002` migration note. Explain what a combined test name alone cannot establish.
