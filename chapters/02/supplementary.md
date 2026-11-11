# Chapter 02 | Supplementary code listings

These are the short code fragments originally printed outside the Practical Laboratory section. They are demonstrations, not an automatically executable standalone program. Consult the chapter's full laboratory for runnable files and commands.

## Listing 1



```python
# Counterexample: do not use as the implementation.
if key in self._by_key and self._by_key[key][0] == kind:
    request_id = self._by_key[key][1]
    self._by_id[request_id] = (kind, "submitted")
    return request_id
```

