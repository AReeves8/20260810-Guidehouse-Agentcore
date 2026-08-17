# Restock Validator — Week 1 Assignment Reference Solution

A reference implementation of the Week 1 assignment (`assignments/week-01/ASSIGNMENT.md`):
a Pydantic v2 model, a custom exception hierarchy, and a defensive loader
that validates a warehouse's restock manifest, skipping bad rows instead
of crashing on them.

**This is one valid way to structure the project, not the only one.** The
assignment deliberately doesn't dictate a file-by-file layout — if your
own submission split things up differently (e.g. one module instead of
three, or a different test file name) and it meets the assignment's
requirements, it's still correct. Compare approaches, don't just check
for an exact match.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate      # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the tests

```bash
pytest -v
```

## Project layout

```
restock_validator/
    models.py       # RestockItem — the Pydantic v2 model
    exceptions.py   # ManifestError (base) / ManifestNotFoundError
    loader.py       # load_manifest() — the skip-and-log validation boundary
data/
    restock_manifest.json   # the provided fixture, copied in unmodified
tests/
    conftest.py     # shared valid_row fixture
    test_loader.py  # the pytest suite
```

## Design notes

- **Why three files instead of one:** `models.py`, `exceptions.py`, and
  `loader.py` are separated by responsibility — the same single-responsibility
  reasoning behind this week's `support_api` package (`models.py`, `store.py`,
  `filters.py` as separate modules). A model, an exception hierarchy, and a
  loading function change for different reasons, so they live in different files.
- **Why `ManifestNotFoundError` wraps `FileNotFoundError` instead of letting
  it propagate:** callers of `load_manifest` should only ever need to catch
  this module's own exception type, not know or care that the current
  implementation happens to read from a local file. `raise ... from exc`
  keeps the original traceback visible underneath.
- **Why bad rows are skipped and reported, not fatal:** a single malformed
  row (a missing `sku`, an out-of-range `quantity`) is realistic in any
  batch this size — the loader's job is to get you every row that's
  usable, plus a clear report of what wasn't, not to abort the whole
  manifest over one bad line.
- **Why the "missing manifest" test uses `tmp_path`, not a hardcoded path:**
  `tmp_path` (a built-in pytest fixture) guarantees the path doesn't exist
  without depending on anything about the machine running the test.
