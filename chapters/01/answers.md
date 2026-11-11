# Chapter 01 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Key normalisation is a policy decision. In the canonical Chapter 01 handler, compare the stored key handling with two inputs such as `"case-A"` and `" case-A "`. If whitespace is stripped, they collapse to one identity and a conflicting kind must still be rejected. An alternative is literal, case-sensitive comparison. Migrating after release requires deciding whether old keys are rewritten, mapped, or permanently grandfathered, and testing collisions before deployment.

## Question 2

Specify: after a request reaches `decided`, `kind_after == kind_before` for every permitted operation. Construct a test: submit a `permit`, advance to `under_review` and `decided`, save the record, attempt a kind-changing operation or apply an intentional mutant, then assert `get(id).kind` is unchanged. A submission-only test exercises no post-decision mutation.

## Question 3

Propose v1.1 with `enquiry` in the accepted-kind set and an explicit test for successful submission. Against the unmodified v1.0 implementation, the test must fail with the old invalid-kind result; after the smallest implementation and specification change, it should pass. Record the actual command, exit status, commit/hash, invariant and test mapping. Stakeholder authorisation remains a separate gate.

## Question 4

In-memory passing tests do not establish production identity verification, server-side authorisation, persistence, concurrency, HTTP routing or auditability. Provide an identity-provider integration test, a server-side denial test with a forged role claim, storage transaction/restart tests and appropriate threat-model review. Neither a role string nor a green local suite approves production.

## Question 5

A replay-response policy must state whether the latest state or the original response is returned. Returning the latest state exposes updated progress; replaying the original response offers a stable byte-level response but can hide later decisions. Specify the choice and test initial submission, replay before/after permitted transitions and conflict rejection. Do not retroactively attribute the new policy to v1.0.

