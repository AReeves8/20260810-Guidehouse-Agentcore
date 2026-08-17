import pytest


@pytest.fixture
def valid_row() -> dict:
    # A fresh dict per call — several tests mutate the row they're given
    # before validating it, and a single shared dict would leak one test's
    # mutation into the next.
    return {
        "sku": "SKU-9999",
        "warehouse": "west-1",
        "quantity": 10,
        "unit_cost": 5.00,
        "category": "electronics",
    }
