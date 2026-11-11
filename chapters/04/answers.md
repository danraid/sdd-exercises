# Chapter 04 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Sequential in-memory execution excludes two simultaneous replays. A persistent implementation could read the key as absent in two transactions and create two IDs. An atomic uniqueness constraint and transaction/isolation policy are needed; the abstract invariant does not prove their correct implementation.

## Question 2

State `for every key in key_index, record_index[key_index[key]] exists`. Create a key and record, delete the record without deleting the key, and assert index consistency. The assertion detects one counterexample, not every reachable state.

## Question 3

First specify the new decided-state replay prohibition, including what must remain unchanged on rejection; then add a test that fails on the old unconditional-replay handler. Update the version and contract validator, implement rejection, and ensure earlier lifecycle/reviewer tests continue to pass. Explain explicitly that this is a breaking change to previous replay semantics.

## Question 4

A `pass`-only method with a valid name demonstrates that structural link resolution is not semantic coverage. The validator can succeed, but independent assertion review and an execution record are still needed. Neither one automatically grants a human policy approval.

