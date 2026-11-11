# Chapter 05 | Exercises and knowledge checks

**1. Model and assumption.** Draw a two-state model with `active` and `withdrawn` states. Add submit, replay and withdrawal transitions under the laboratory assumptions. Explain what changes if authorised reinstatement is permitted. A satisfactory answer revises the terminal-state invariant rather than adding a contradictory transition.

**2. Invariant and failing test.** Run the stored-state assertion against `ShallowReplayAtlas` without the `assertRaises` wrapper. It should fail because the observed status is `active`. Restore the wrapper or use a separate test before capturing the intended passing suite.

**3. Structural versus semantic links.** Replace one linked test body with `pass` and rerun the overlay. Explain why name resolution can still succeed and why the resulting pass weakens behavioural evidence. Restore the original test and verify that its digest returns to the digest for the restored bytes.

**4. Extend the laboratory.** State a policy for withdrawing a missing key, then implement and test it. Check both the response and resulting state. Record whether your choice is a new requirement or a clarification; do not silently treat it as authorised policy.

**5. Decide the gate.** A run has valid recorded hashes and five passing tests, but no reviewer has approved terminal withdrawal. Identify the gates with evidence. Structural resolution and bounded behavioural execution have recorded results; policy approval remains unrecorded.
