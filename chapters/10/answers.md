# Chapter 10 | Model answers and marking guidance

These are worked model responses. Where an exercise calls for code execution, record real output and hashes; do not represent predicted output as observed evidence. The synthetic Atlas role string never establishes production authentication.

## Question 1

An untrusted string `reviewer` is not authentication. Deployed enforcement needs a verified identity/token boundary, server-side authorisation, audit logging and protected storage. Define the threat model and check role changes/revocations.

## Question 2

Capture state, invoke a deliberately faulty advance that changes state then raises `PermissionError`, and assert the expected exception plus unchanged full snapshot. The exception alone cannot establish that no side effect happened.

## Question 3

Changing a linked test body to `pass` can leave the method name valid. The structural resolver therefore still accepts it, while the obligation has no behavioural oracle. Restore positive and negative assertions and independently inspect the result.

## Question 4

Add a second request, save both snapshots and the ID counter, then perform a rejected advancement of the first. Assert snapshots and counter are identical after rejection. Re-run the suite and record hashes. No conclusion extends to authentication, real storage or concurrency.

## Question 5

A classroom decision should identify an actual authorised approver, candidate commit/hash, specification version, executed evidence and accepted limitations. Without observed tests or an authorised person, use `PENDING`. Never reuse classroom acceptance as permission to deploy.

