"""Defensive loading of a warehouse restock manifest: skip-and-log validation boundary."""

import json
from pathlib import Path

from pydantic import ValidationError

from .exceptions import ManifestNotFoundError
from .models import RestockItem


def load_manifest(path: Path | str) -> tuple[list[RestockItem], list[dict]]:
    """Return (valid_items, error_report). A bad row is recorded and skipped, never fatal."""
    resolved = Path(path)

    try:
        raw_text = resolved.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        # Translate the stdlib exception into this module's own vocabulary —
        # chained with `from exc` so the original traceback is still visible —
        # so callers only ever need to catch ManifestNotFoundError, regardless
        # of whether the manifest ever moves off the local filesystem.
        raise ManifestNotFoundError(f"No restock manifest at {resolved}") from exc

    rows = json.loads(raw_text)

    valid: list[RestockItem] = []
    errors: list[dict] = []
    for row in rows:
        try:
            valid.append(RestockItem.model_validate(row))
        except ValidationError as exc:
            # One bad row is recorded and the loop moves on — a missing sku
            # or an out-of-range quantity shouldn't cost you the other 11
            # rows in the batch.
            messages = [f"{e['loc'][0]}: {e['msg']}" for e in exc.errors()]
            errors.append({"sku": row.get("sku", "<no sku>"), "errors": messages})

    return valid, errors
