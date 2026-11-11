# Chapter 07 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

Validation before delegation prevents an LLM- or caller-supplied description from being passed to a side-effecting operation before the contract is checked. Retaining descriptions in stored records requires schema, persistence, trust-boundary, migration and test changes, not just a wrapper change.

## Question 2

Implement a mutant that invokes the delegate and only then validates the input. Assert that rejection leaves the entire delegate call log and persistent state unchanged. An exception-only test may still pass after a prohibited side effect has occurred.

## Question 3

Propose a 100-character maximum with 100 accepted and 101 rejected, and define treatment of Unicode code points vs bytes. Add a new requirement ID, link to a genuine test and update the validator/version. The outcome is a synthetic proposal until independently run and authorised.

## Question 4

Linking a requirement to an existing but irrelevant test can pass structural name resolution. Semantic review must inspect what the test asserts and show that the stated invariant, inputs and negative cases are actually observed.

