# Chapter 11 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Structural resolution shows names are present; tests show exercised behaviour for identified bytes; a CI green run alone is not a human-approved release. Separate approval introduces latency but is necessary where safety/security requirements are hard gates.

## Question 2

Conflicting replay must raise the defined error and leave original ID, kind and current state unchanged. Advance a request first, snapshot it, inject an implementation mutant that changes state before raising, and assert equality afterwards to expose the defect.

## Question 3

Create the two proposed files, record SHA-256 checksums and environment, run `python -m unittest -v test_delivery`, then deliberately break and restore one test link. Save the actual failing and passing outputs. Expected outcomes in the chapter are not observations without a run.

## Question 4

Inspect v1.0's two REQ-002 tests and v1.1's combined method assertions. The renamed link can improve navigation but does not prove equivalent semantics. Chapter 04 uses a distinct stand-alone mapping and cannot stand in for Chapter 03.

## Question 5

Bind policy approval to an immutable candidate and deployment artefact digest, full specification and test evidence, role-authorised reviewer and timestamp. Missing approval means hold, not inferred consent from test results.

