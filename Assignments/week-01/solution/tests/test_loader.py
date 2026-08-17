from pathlib import Path

import pytest
from pydantic import ValidationError

from restock_validator.exceptions import ManifestNotFoundError
from restock_validator.loader import load_manifest
from restock_validator.models import RestockItem

MANIFEST_PATH = Path(__file__).parent.parent / "data" / "restock_manifest.json"


def test_valid_row_loads_correctly(valid_row):
    item = RestockItem.model_validate(valid_row)
    assert item.sku == "SKU-9999"
    assert item.category == "electronics"


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("category", "furniture"),  # outside the allowed Literal set
        ("quantity", -5),  # must be > 0
        ("unit_cost", 0),  # must be > 0
    ],
)
def test_rejects_invalid_field_values(valid_row, field, bad_value):
    valid_row[field] = bad_value
    with pytest.raises(ValidationError):
        RestockItem.model_validate(valid_row)


def test_provided_manifest_returns_expected_valid_and_error_counts():
    # The provided restock_manifest.json is a fixed, 12-row batch: 8 valid
    # rows and 4 deliberately broken ones (bad category, negative quantity,
    # zero unit_cost, missing sku). This is the proof the loader handles a
    # realistic, mixed-quality batch correctly — not just a single clean row.
    valid, errors = load_manifest(MANIFEST_PATH)
    assert len(valid) == 8
    assert len(errors) == 4


def test_missing_manifest_raises_custom_exception(tmp_path):
    with pytest.raises(ManifestNotFoundError):
        load_manifest(tmp_path / "does-not-exist.json")
