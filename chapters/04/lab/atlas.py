from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Record:
    kind: str
    state: str


class Atlas:
    KINDS = {"permit", "appointment"}
    NEXT = {
        "submitted": "under_review",
        "under_review": "decided",
    }

    def __init__(self):
        self._keys = {}
        self._records = {}
        self._next_id = 1

    def submit(self, key, kind):
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-blank string")
        if kind not in self.KINDS:
            raise ValueError("unknown kind")

        if key in self._keys:
            request_id = self._keys[key]
            if self._records[request_id].kind != kind:
                raise ValueError("conflicting replay")
            return request_id

        request_id = self._next_id
        self._next_id += 1
        self._keys[key] = request_id
        self._records[request_id] = Record(kind, "submitted")
        return request_id

    def get(self, request_id):
        return self._records[request_id]

    def advance(self, request_id, target, role):
        if role != "reviewer":
            raise PermissionError("reviewer role required")
        record = self._records[request_id]
        if self.NEXT.get(record.state) != target:
            raise ValueError("invalid transition")
        self._records[request_id] = replace(record, state=target)
