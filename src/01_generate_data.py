"""Generate reproducible synthetic inventory data for StockWise.

Run from the repository root:
    python src/01_generate_data.py

The script writes five CSV files to data/raw/. The generated records are
synthetic teaching data and do not describe a real company.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


def add_controlled_quality_issues(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Inject documented data-quality issues for the cleaning stage."""
    # Exact duplicate records.
    for name in ("products", "suppliers", "purchase_orders", "stock_movements"):
        frame = frames[name]
        frames[name] = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)

    # Missing values in descriptive and measure fields.
    frames["products"].loc[5, "category"] = np.nan
    frames["suppliers"].loc[3, "region"] = np.nan
    frames["inventory"].loc[7, "reserved_quantity"] = np.nan
    frames["purchase_orders"].loc[11, "expected_delivery_date"] = ""

    # Invalid values and inconsistent labels for the cleaning exercise.
    frames["products"].loc[9, "unit_cost"] = -12.50
    frames["inventory"].loc[13, "available_quantity"] = -9999
    frames["stock_movements"].loc[17, "movement_type"] = " issue "
    frames["products"].loc[14, "category"] = " home & kitchen "
    frames["suppliers"].loc[6, "region"] = " north "
    return frames


def generate_data(seed: int = SEED) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    supplier_count = 12
    product_count = 80

    regions = ["North", "South", "East", "West", "Central"]
    suppliers = pd.DataFrame({
        "supplier_id": [f"SUP{i:03d}" for i in range(1, supplier_count + 1)],
        "supplier_name": [f"Supplier {i:02d}" for i in range(1, supplier_count + 1)],
        "region": rng.choice(regions, supplier_count),
        "rating": np.round(rng.uniform(2.8, 5.0, supplier_count), 1),
    })

    categories = ["Electronics", "Grocery", "Home & Kitchen", "Stationery", "Personal Care"]
    products = pd.DataFrame({
        "product_id": [f"PRD{i:04d}" for i in range(1, product_count + 1)],
        "sku": [f"SKU-{i:05d}" for i in range(1, product_count + 1)],
        "product_name": [f"Product {i:03d}" for i in range(1, product_count + 1)],
        "category": rng.choice(categories, product_count),
        "unit_cost": np.round(rng.uniform(35, 4500, product_count), 2),
        "reorder_level": rng.integers(12, 65, product_count),
        "supplier_id": rng.choice(suppliers["supplier_id"], product_count),
    })

    today = pd.Timestamp("2026-11-25")
    start = today - pd.Timedelta(days=89)
    dates = pd.date_range(start, today, freq="D")
    movement_rows = []
    movement_id = 1
    for product_id in products["product_id"]:
        event_days = rng.choice(dates, size=22, replace=True)
        for event_date in event_days:
            movement_type = rng.choice(["IN", "OUT"], p=[0.43, 0.57])
            quantity = int(rng.integers(1, 36))
            movement_rows.append({
                "movement_id": f"MOV{movement_id:06d}",
                "product_id": product_id,
                "movement_date": pd.Timestamp(event_date).strftime("%Y-%m-%d"),
                "movement_type": movement_type,
                "quantity": quantity,
                "reference": f"REF-{movement_id:06d}",
            })
            movement_id += 1
    stock_movements = pd.DataFrame(movement_rows)

    opening = rng.integers(45, 180, product_count)
    signed = np.where(stock_movements["movement_type"].eq("IN"),
                      stock_movements["quantity"], -stock_movements["quantity"])
    movement_net = pd.Series(signed, index=stock_movements["product_id"]).groupby(level=0).sum()
    available = [int(max(-8, opening[i] + movement_net.get(pid, 0)))
                 for i, pid in enumerate(products["product_id"])]
    received = (stock_movements[stock_movements["movement_type"].eq("IN")]
                .groupby("product_id")["quantity"].sum()
                .reindex(products["product_id"], fill_value=0).to_numpy())
    issued = (stock_movements[stock_movements["movement_type"].eq("OUT")]
              .groupby("product_id")["quantity"].sum()
              .reindex(products["product_id"], fill_value=0).to_numpy())
    inventory = pd.DataFrame({
        "inventory_id": [f"INV{i:04d}" for i in range(1, product_count + 1)],
        "product_id": products["product_id"],
        "snapshot_date": today.strftime("%Y-%m-%d"),
        "opening_quantity": opening,
        "received_quantity": received,
        "issued_quantity": issued,
        "reserved_quantity": rng.integers(0, 12, product_count),
        "available_quantity": available,
    })

    po_rows = []
    for order_no in range(1, 241):
        product = products.iloc[int(rng.integers(0, product_count))]
        order_date = start + pd.Timedelta(days=int(rng.integers(0, 85)))
        expected_days = int(rng.integers(3, 12))
        actual_delay = int(rng.choice([-2, -1, 0, 1, 2, 3, 5, 8],
                                      p=[.08, .08, .25, .18, .15, .12, .09, .05]))
        expected_date = order_date + pd.Timedelta(days=expected_days)
        actual_date = expected_date + pd.Timedelta(days=actual_delay)
        po_rows.append({
            "order_id": f"PO{order_no:05d}",
            "supplier_id": product["supplier_id"],
            "product_id": product["product_id"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "expected_delivery_date": expected_date.strftime("%Y-%m-%d"),
            "actual_delivery_date": actual_date.strftime("%Y-%m-%d"),
            "quantity_ordered": int(rng.integers(15, 180)),
            "unit_cost": float(product["unit_cost"]),
        })
    purchase_orders = pd.DataFrame(po_rows)

    return add_controlled_quality_issues({
        "products": products,
        "suppliers": suppliers,
        "inventory": inventory,
        "purchase_orders": purchase_orders,
        "stock_movements": stock_movements,
    })


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    frames = generate_data()
    for name, frame in frames.items():
        path = RAW_DIR / f"{name}.csv"
        frame.to_csv(path, index=False)
        print(f"Created {path.relative_to(BASE_DIR)}: {len(frame):,} rows, {len(frame.columns)} columns")
    print(f"Synthetic data generated with fixed seed {SEED}.")


if __name__ == "__main__":
    main()
