# Chapter 09 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Gate 1 rejects absent/dangling/irrelevant test references. Gate 2 rejects a test failure, stale executable or missing observation. Gate 3 rejects missing or unauthorised policy approval. These cannot be averaged into one score.

## Question 2

State that conflicting key reuse cannot alter either the original record or unrelated records. Create two requests, mutate the second in a deliberate defective conflict handler, and assert deep equality for both before/after. Restore the handler and verify the test catches the mutant.

## Question 3

Start from the actual Chapter 03 files in `sdd/examples/atlas_ch03/`. Compare spec contents, generate the separate proposed candidate and run the documented capture. Record command, Python version, hashes and observed outcome. Inject a dangling test reference and verify structural failure. The proposed extension is not canonical until integrated and tested.

## Question 4

The string `1.2` is just a label. A correct change record needs the source/destination specification identities, resolved assertions, actual test run for the candidate, review of behaviour and a signed/authorised policy decision. A hash verifies bytes, not their meaning or approval.

