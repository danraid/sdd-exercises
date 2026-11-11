# Chapter 01 | Exercises and knowledge checks

1. **Assumptions and trade-offs.** The laboratory strips whitespace from idempotency keys. Explain how this choice affects two otherwise distinct client inputs. Propose an alternative and describe the compatibility consequences of changing it after release.

2. **Invariant and failing test.** A new requirement says that a decided request must retain its kind permanently. State an invariant, then write a test that would fail for an implementation that changes the kind during advancement. Explain why a passing test of the initial submission alone is insufficient.

3. **Change and trace.** Introduce a third kind, `enquiry`, in a proposed specification v1.1. Write the acceptance test first, record its result against v1.0, implement the smallest change and rerun the suite. Record `requirement → invariant → test → result`, including the actual revision and output. Identify any stakeholder or policy approval still needed.

4. **Evidence analysis.** A team reports that every Atlas test passes and concludes that unauthorised staff cannot change production requests. Identify at least three assumptions missing from that inference. Propose separate evidence for identity, authorisation and the persistence boundary.

5. **Specification review.** Decide whether a replay after advancement should return the current record or the original response. Specify your choice precisely, including its consequences for clients, and describe how you would test it. Compare your choice with v1.0 rather than silently changing the contract.
