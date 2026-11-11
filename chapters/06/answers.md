# Chapter 06 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Returning the same object in a sequential model can preserve state but does not provide transactional atomicity across processes. A durable, concurrent system needs uniqueness, locking/transactions, recovery guarantees and separate tests for race and restart sequences.

## Question 2

Extend the record with `priority`, advance a request, change priority, then replay. Snapshot the complete record before retry and assert equality afterwards. A mutant that reinitialises priority preserves ID and fools a shallow identity-only assertion but fails the snapshot comparison.

## Question 3

Add `REQ-007` with an explicit priority-preservation invariant, positive replay test and negative mutation test. Update expected IDs and derivation/validator logic; first verify a dangling link fails, then run the amended suite and capture genuine results. Keep policy approval as a separate step.

## Question 4

Audit the actual Chapter 01 and Chapter 03 specifications, test source, commit history, hashes and any signed approval record. The combined REQ-002 test name in v1.1 alone says nothing about equivalent assertion coverage or historical acceptance.

