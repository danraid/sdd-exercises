# Chapter 08 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Treating `principal` as a trusted input makes key scope testable without implementing authentication. It does not establish that callers cannot forge the principal or that storage is tenant-isolated. A deployment needs trusted identity propagation, database isolation and concurrency tests.

## Question 2

Define success as `after_replay == before_replay` for `records` and `next_receipt`, with the same returned ID. Insert a mutant that increments the counter on replay; the deeper snapshot test should fail even if ID equality holds.

## Question 3

Replacing REQ-006's link with the existing REQ-002 test name can satisfy a name-only validator but does not exercise principal scoping. Review the test body, then restore a link to actual cross-principal assertions and run them.

## Question 4

Propose REQ-007 that an empty key fails without changing state; define whether whitespace-only counts as empty. Expand the version and expected IDs, add accepted/rejected cases and test a deliberate dangling link. Retain candidate hashes, observed status and a separate pending policy decision.

