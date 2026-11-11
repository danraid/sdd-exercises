class Atlas:
    def __init__(self):
        self._by_key = {}  # key -> (kind, ID)
        self._by_id = {}   # ID -> (kind, state)
        self._next_id = 1

    def submit(self, key, kind):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("non-blank string key required")
        if kind not in ("permit", "appointment"):
            raise ValueError("unsupported kind")
        if key in self._by_key:
            old_kind, request_id = self._by_key[key]
            if kind != old_kind:
                raise ValueError("conflicting replay")
            return request_id

        request_id = f"R-{self._next_id:04d}"
        self._next_id += 1
        self._by_key[key] = (kind, request_id)
        self._by_id[request_id] = (kind, "submitted")
        return request_id

    def read(self, request_id):
        return self._by_id[request_id]

    def advance(self, request_id, role, target):
        if role != "reviewer":
            raise PermissionError("reviewer required")
        kind, state = self._by_id[request_id]
        allowed = {
            "submitted": "under_review",
            "under_review": "decided",
        }
        if state not in allowed or target != allowed[state]:
            raise ValueError("invalid transition")
        self._by_id[request_id] = (kind, target)
