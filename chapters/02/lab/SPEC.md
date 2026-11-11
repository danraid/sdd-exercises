Atlas specification v1.1
Scope: sequential, in-memory; no network or authentication.
REQ-001: kinds are permit and appointment.
REQ-002: matching key and kind return the original ID; conflict fails.
REQ-003: submitted -> under_review -> decided; no other transitions.
REQ-004: only the reviewer role string may advance.
REQ-005: matching replay preserves lifecycle state.
Local: non-blank keys compare exactly; IDs are allocated sequentially.
