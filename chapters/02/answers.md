# Chapter 02 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Under the exercise's literal-key policy, `case-A` and ` case-A ` are distinct and can acquire different IDs. Trimming would merge them and risk collisions with existing persisted keys. Change specification, implementation and acceptance tests together, including leading/trailing-space and conflicting-kind pairs; document migration impact.

## Question 2

Specify `on conflicting replay: stored_record_after == stored_record_before`. Submit a permit, advance to `under_review`, deep-copy the record, then replay the same key with kind `appointment` and assert `ValueError` plus complete state equality. A mutant that resets state before raising should fail the equality assertion.

## Question 3

Version the proposal as v1.2 and state that permitted key length is 1–32 characters (subject to the chosen blankness rule). Add boundary cases length 32 accepted and length 33 rejected before the implementation edit; update any validator snapshot/version gate. Record hashes and actual run results, and explicitly resolve whether existing overlong keys may replay.

## Question 4

Six passing tests for an in-memory model cannot establish deployed security. The role string is not authenticated identity, the object has no HTTP/network exposure, and sequential tests do not test racing submissions or durable storage. The correct gate is bounded classroom behaviour only, with a separate policy decision.

