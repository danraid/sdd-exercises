# Chapter 05 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

A two-state model has `active` and `withdrawn`; submit creates an active record, replay should preserve existing state, and withdraw transitions active to withdrawn. With terminal withdrawal, no transition leaves withdrawn. If reinstatement is permitted, remove the terminal invariant, specify who may reinstate, add negative tests and revise the state machine.

## Question 2

Use `ShallowReplayAtlas` as a deliberate mutant: after withdrawal, replay resets status to active. Without an `assertRaises(AssertionError)` wrapper, a full-state equality assertion should fail. Restore the wrapper only for an explicit negative-control test; never interpret it as a successful mutant.

## Question 3

Replace a linked acceptance body with `pass`. A name-only validator will still find the method and can report structural success. That says nothing about the invariant. Restore the meaningful assertion and compare SHA-256 hashes of the restored bytes to establish file identity.

## Question 4

For missing-key withdrawal, choose either `KeyError` with no mutation or an explicitly idempotent no-op. Document the policy, add both success and failure cases, and test counter/key/record snapshots. Treat the new choice as a proposal requiring approval.

## Question 5

Hashes and passing tests support structural and bounded behavioural evidence, not policy authority. A release decision must identify owner, reviewed artefact digests, tests and dates, and must remain `PENDING` when no authorised person has accepted terminal withdrawal.

