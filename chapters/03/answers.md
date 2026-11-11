# Chapter 03 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Trimming inputs changes the identity relation: `"case-1"` and `" case-1 "` may become the same key. Obtain a product-owner decision covering existing stored keys and new submissions. Test collisions, rejected conflicts and consistent behaviour before/after migration; a version change must not silently rewrite identity.

## Question 2

State the conflict invariant as `record_after == record_before` for the old key, including both ID and current state. Advance `R1`, attempt conflicting reuse, check `ValueError`, then call valid replay and compare the returned `(ID, state)`. Inject a state reset before the error to prove the test fails; restore and rerun.

## Question 3

The proposed REQ-006 must define unknown-ID rejection precisely, including the chosen exception and the no-state-change property. Update spec `version`, `EXPECTED_IDS`, the validator's version check, acceptance method, capture version and trace table together. Preserve existing tests and run one intentional dangling-link check. The resulting execution record must contain actual status and hashes; it cannot authorise policy by itself.

