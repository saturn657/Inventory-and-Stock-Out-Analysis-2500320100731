"""Automated data-quality and reconciliation tests for StockWise."""
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "clean"
REPORT_DIR = BASE_DIR / "reports"


@pytest.fixture(scope="session")
def data():
    names = ["products", "suppliers", "inventory", "purchase_orders", "stock_movements"]
    missing = [name for name in names if not (CLEAN_DIR / f"{name}.csv").exists()]
    if missing:
        pytest.fail(f"Missing clean datasets: {', '.join(missing)}. Run the generator and cleaner first.")
    return {name: pd.read_csv(CLEAN_DIR / f"{name}.csv") for name in names}


def test_primary_keys_are_unique(data):
    keys = {
        "products": "product_id",
        "suppliers": "supplier_id",
        "inventory": "inventory_id",
        "purchase_orders": "order_id",
        "stock_movements": "movement_id",
    }
    for name, key in keys.items():
        assert data[name][key].is_unique, f"{name}.{key} contains duplicates"


def test_required_identifiers_are_present(data):
    required = {
        "products": ["product_id", "sku", "supplier_id"],
        "suppliers": ["supplier_id", "supplier_name"],
        "inventory": ["inventory_id", "product_id"],
        "purchase_orders": ["order_id", "product_id", "supplier_id", "order_date"],
        "stock_movements": ["movement_id", "product_id", "movement_date"],
    }
    for name, columns in required.items():
        for column in columns:
            assert data[name][column].notna().all(), f"{name}.{column} has missing values"


def test_numeric_ranges_and_movement_labels(data):
    products = data["products"]
    inventory = data["inventory"]
    suppliers = data["suppliers"]
    movements = data["stock_movements"]
    orders = data["purchase_orders"]
    assert (products["unit_cost"] >= 0).all()
    assert (products["reorder_level"] >= 0).all()
    assert suppliers["rating"].between(0, 5).all()
    for col in ["opening_quantity", "received_quantity", "issued_quantity", "reserved_quantity"]:
        assert (inventory[col] >= 0).all(), f"Inventory {col} must be non-negative"
    assert (inventory["available_quantity"] > -1000).all()
    assert set(movements["movement_type"].str.upper().unique()) <= {"IN", "OUT"}
    assert (movements["quantity"] > 0).all()
    assert (orders["quantity_ordered"] > 0).all()
    assert (orders["unit_cost"] >= 0).all()


def test_foreign_keys_match_dimension_records(data):
    product_ids = set(data["products"]["product_id"])
    supplier_ids = set(data["suppliers"]["supplier_id"])
    assert set(data["inventory"]["product_id"]) <= product_ids
    assert set(data["stock_movements"]["product_id"]) <= product_ids
    assert set(data["purchase_orders"]["product_id"]) <= product_ids
    assert set(data["products"]["supplier_id"]) <= supplier_ids
    assert set(data["purchase_orders"]["supplier_id"]) <= supplier_ids


def test_purchase_order_dates_are_valid_and_chronological(data):
    orders = data["purchase_orders"].copy()
    for col in ["order_date", "expected_delivery_date", "actual_delivery_date"]:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")
        assert orders[col].notna().all(), f"{col} contains an invalid date"
    assert (orders["expected_delivery_date"] >= orders["order_date"]).all()
    assert (orders["actual_delivery_date"] >= orders["order_date"]).all()


def test_cleaning_log_documents_changes():
    path = REPORT_DIR / "cleaning_log.csv"
    assert path.exists(), "Cleaning log is missing"
    log = pd.read_csv(path)
    assert {"dataset", "issue", "rule_applied", "rows_affected"} <= set(log.columns)
    assert (log["rows_affected"] > 0).all()
    assert log["rule_applied"].notna().all()


def test_python_totals_match_oracle_query_exports(data):
    output_dir = REPORT_DIR / "sql_results"
    required = [
        "Q1_inventory_stock_status_by_product_category.csv",
        "Q3_inventory_value_by_category.csv",
        "Q5_supplier_delivery_performance_and_average_lead_time.csv",
        "Q7_product_level_stock_movement_totals.csv",
    ]
    missing = [name for name in required if not (output_dir / name).exists()]
    if missing:
        pytest.skip(
            "Oracle reconciliation pending; missing actual Oracle query exports: "
            + ", ".join(missing)
        )

    inventory = data["inventory"].merge(
        data["products"], on="product_id", validate="one_to_one"
    )
    stockout = int((inventory["available_quantity"] <= 0).sum())
    low_stock = int((
        (inventory["available_quantity"] > 0)
        & (inventory["available_quantity"] <= inventory["reorder_level"])
    ).sum())
    available = int(inventory["available_quantity"].sum())
    value = float((inventory["available_quantity"] * inventory["unit_cost"]).sum())
    q1 = pd.read_csv(output_dir / required[0])
    q3 = pd.read_csv(output_dir / required[1])
    q5 = pd.read_csv(output_dir / required[2])
    q7 = pd.read_csv(output_dir / required[3])
    assert int(q1["product_count"].sum()) == data["products"]["product_id"].nunique()
    assert int(q1["stockout_products"].sum()) == stockout
    assert int(q1["low_stock_products"].sum()) == low_stock
    assert int(q1["total_available_quantity"].sum()) == available
    assert abs(float(q3["inventory_value"].sum()) - value) < 0.01
    assert int(q5["delivered_orders"].sum()) == len(data["purchase_orders"])
    delayed = (
        pd.to_datetime(data["purchase_orders"]["actual_delivery_date"])
        > pd.to_datetime(data["purchase_orders"]["expected_delivery_date"])
    ).sum()
    assert int(q5["delayed_orders"].sum()) == int(delayed)
    assert int(q7["units_received"].sum()) == int(
        data["stock_movements"].loc[data["stock_movements"]["movement_type"] == "IN", "quantity"].sum()
    )
    assert int(q7["units_issued"].sum()) == int(
        data["stock_movements"].loc[data["stock_movements"]["movement_type"] == "OUT", "quantity"].sum()
    )
