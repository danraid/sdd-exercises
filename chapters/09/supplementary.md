# Chapter 09 | Supplementary code listings

These are the short code fragments originally printed outside the Practical Laboratory section. They are demonstrations, not an automatically executable standalone program. Consult the chapter's full laboratory for runnable files and commands.

## Listing 1



```python
if key in keys and keys[key]["kind"] != kind:
    records[keys[key]["id"]]["state"] = "submitted"  # defect
    raise ValueError("conflicting key")
```

