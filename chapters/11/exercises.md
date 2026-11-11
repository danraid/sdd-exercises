# Chapter 11 | Exercises and knowledge checks

1. **Assumptions and trade-offs.** A pipeline validates test names, runs tests and automatically deploys on green. Identify the evidence each stage supplies and the missing authorised decision. Explain one operational cost of separating approval from execution and why a hard invariant should not become a weighted score.

2. **Invariant and failing test.** Write an invariant for conflicting replay: rejecting a different kind under an existing key must not alter the existing request. Construct a test that advances a request first, attempts a conflicting replay, and checks both the exception and retained state. Describe a mutant that your test should reject.

3. **Implement and verify.** Create the proposed laboratory files, run the checks, and record input hashes, Python version, command, output and exit status. Deliberately introduce a dangling link and retain the failure record. Restore it and run again. Report observations separately from the expected outcomes stated above.

4. **Review a trace migration.** Compare Chapter 01’s two REQ-002 test names with Chapter 03’s combined name. Explain why a documented rename helps navigation but does not prove equivalent assertions. Why is the Chapter 04 stand-alone REQ-002 link not a substitute for the Chapter 03 mapping?

5. **Authorisation.** Draft a release record that binds a policy decision to a candidate revision, specification digest, test record and—if one exists—deployment artefact digest. State who is authorised to approve it and what happens when approval is absent.
