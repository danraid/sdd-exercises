# Chapter 12 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Literal key comparison distinguishes `A` and `a` as well as `key` and ` key `. Trimming or Unicode normalisation can reduce accidental duplicates but may merge keys previously distinct. Specify and test collisions and migration behaviour explicitly.

## Question 2

State that a conflicting replay leaves ID, kind and progress unchanged. Advance a request, snapshot the record, attempt a conflicting-kind retry, assert `ValueError` and full equality. A mutant that resets progress before raising fails the post-error snapshot check.

## Question 3

Add REQ-006 for non-blank ASCII keys up to 32 characters, with boundaries for 0, 1, 32, 33 and non-ASCII input, and verify both new submissions and replays. Keep the baseline requirements, run structural and behavioural tests, record actual hashes and status, and separately note whether an authorised policy owner approved the proposal.

## Question 4

A test-pass report lacks artefact identity and version binding, coverage scope, environment and output records, and a policy-owner decision. Approval cannot be inferred from linked test names or a green job. Require evidence tied to the actual candidate and authorised reviewer.

