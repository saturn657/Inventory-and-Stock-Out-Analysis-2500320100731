"""Create static StockWise inventory and supplier analysis charts.

Run from the repository root after data generation and cleaning:
    python src/04_analysis_charts.py

Charts are written to reports/charts/ as PNG files.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "clean"
CHART_DIR = BASE_DIR / "reports" / "charts"


def load_data():
    required = ["products", "inventory", "suppliers", "purchase_orders", "stock_movements"]
    missing = [name for name in required if not (CLEAN_DIR / f"{name}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing cleaned datasets: {', '.join(missing)}. Run src/02_clean_data.py first."
        )
    products = pd.read_csv(CLEAN_DIR / "products.csv")
    inventory = pd.read_csv(CLEAN_DIR / "inventory.csv")
    suppliers = pd.read_csv(CLEAN_DIR / "suppliers.csv")
    orders = pd.read_csv(
        CLEAN_DIR / "purchase_orders.csv",
        parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"]
    )
    movements = pd.read_csv(
        CLEAN_DIR / "stock_movements.csv", parse_dates=["movement_date"]
    )
    return products, inventory, suppliers, orders, movements


def main():
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    products, inventory, suppliers, orders, movements = load_data()

    # Business rule: inventory value = available quantity * unit cost.
    # Negative available quantity is retained because it identifies stock-outs.
    stock = inventory.merge(products, on="product_id", how="left", validate="one_to_one")
    stock["inventory_value"] = stock["available_quantity"] * stock["unit_cost"]
    stock["stock_status"] = np.select(
        [
            stock["available_quantity"] <= 0,
            (stock["available_quantity"] > 0)
            & (stock["available_quantity"] <= stock["reorder_level"]),
        ],
        ["Stock-out", "Low stock"],
        default="Healthy",
    )

    # 1. Available stock by category.
    category_stock = (
        stock.groupby("category", as_index=False)["available_quantity"]
        .sum().sort_values("available_quantity")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(category_stock["category"], category_stock["available_quantity"])
    ax.set_title("Available Inventory by Category")
    ax.set_xlabel("Available units")
    ax.set_ylabel("Product category")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "01_available_stock_by_category.png", dpi=160)
    plt.close(fig)

    # 2. Product stock status counts by category.
    status_counts = stock.groupby(["category", "stock_status"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    status_counts.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Stock Status by Category")
    ax.set_xlabel("Product category")
    ax.set_ylabel("Number of products")
    ax.legend(title="Stock status")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "02_stock_status_by_category.png", dpi=160)
    plt.close(fig)

    # 3. Monthly stock movement trend. IN and OUT are shown separately.
    movements["month"] = movements["movement_date"].dt.to_period("M").astype(str)
    monthly = movements.pivot_table(
        index="month", columns="movement_type", values="quantity",
        aggfunc="sum", fill_value=0
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    for movement_type in ["IN", "OUT"]:
        if movement_type in monthly.columns:
            ax.plot(monthly.index, monthly[movement_type], marker="o", label=movement_type)
    ax.set_title("Monthly Stock Movement Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Units moved")
    ax.legend(title="Movement")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "03_monthly_stock_movement.png", dpi=160)
    plt.close(fig)

    # 4. Supplier lead time = actual delivery date - order date.
    orders["lead_time_days"] = (
        orders["actual_delivery_date"] - orders["order_date"]
    ).dt.days
    orders["is_delayed"] = (
        orders["actual_delivery_date"] > orders["expected_delivery_date"]
    )
    supplier_perf = (
        orders.groupby("supplier_id", as_index=False)
        .agg(
            avg_lead_time_days=("lead_time_days", "mean"),
            delayed_orders=("is_delayed", "sum"),
            order_count=("order_id", "count"),
        )
        .merge(suppliers[["supplier_id", "supplier_name"]],
               on="supplier_id", how="left")
        .sort_values("avg_lead_time_days")
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(supplier_perf["supplier_name"], supplier_perf["avg_lead_time_days"])
    ax.set_title("Average Supplier Delivery Lead Time")
    ax.set_xlabel("Average lead time (calendar days)")
    ax.set_ylabel("Supplier")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "04_supplier_lead_time.png", dpi=160)
    plt.close(fig)

    # 5. Reorder gap = reorder level - available quantity; positive means below threshold.
    stock["reorder_gap"] = stock["reorder_level"] - stock["available_quantity"]
    risk = (
        stock.sort_values("reorder_gap", ascending=False)
        .head(15).sort_values("reorder_gap")
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(risk["product_name"], risk["reorder_gap"])
    ax.set_title("Top 15 Products with Highest Reorder Gap")
    ax.set_xlabel("Reorder level minus available quantity (units)")
    ax.set_ylabel("Product")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "05_top_reorder_risks.png", dpi=160)
    plt.close(fig)

    # 6. Inventory value by category, using the documented metric definition.
    category_value = (
        stock.groupby("category", as_index=False)["inventory_value"]
        .sum().sort_values("inventory_value")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(category_value["category"], category_value["inventory_value"])
    ax.set_title("Inventory Value by Category")
    ax.set_xlabel("Inventory value (dataset currency units)")
    ax.set_ylabel("Product category")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "06_inventory_value_by_category.png", dpi=160)
    plt.close(fig)

    # 7. Estimated stock-out trend from opening stock and dated movements.
    # Assumption: opening_quantity is the starting balance at the beginning of
    # the movement window; each IN adds units and each OUT subtracts units.
    # This is a reconstructed daily balance, not a live daily inventory snapshot.
    all_days = pd.date_range(
        movements["movement_date"].min(),
        movements["movement_date"].max(),
        freq="D",
    )
    movement_daily = movements.copy()
    movement_daily["signed_quantity"] = np.where(
        movement_daily["movement_type"].eq("IN"),
        movement_daily["quantity"],
        -movement_daily["quantity"],
    )
    movement_daily = movement_daily.groupby(
        ["product_id", "movement_date"]
    )["signed_quantity"].sum()
    opening_stock = inventory.set_index("product_id")["opening_quantity"]
    daily_stockout_counts = pd.Series(0, index=all_days, dtype="int64")
    for product_id, opening_qty in opening_stock.items():
        product_moves = movement_daily.xs(product_id, level="product_id")
        daily_net = product_moves.reindex(all_days, fill_value=0)
        daily_balance = int(opening_qty) + daily_net.cumsum()
        daily_stockout_counts += (daily_balance <= 0).astype("int64")
    monthly_stockouts = daily_stockout_counts.groupby(
        daily_stockout_counts.index.to_period("M")
    ).mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_stockouts.index.astype(str), monthly_stockouts.values, marker="o")
    ax.set_title("Estimated Average Daily Stock-Out Products by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average number of products at zero or negative stock")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(CHART_DIR / "07_estimated_stockout_trend.png", dpi=160)
    plt.close(fig)

    outputs = sorted(CHART_DIR.glob("*.png"))
    if len(outputs) < 5:
        raise RuntimeError(f"Expected at least 5 charts, found {len(outputs)}.")
    for path in outputs:
        if path.stat().st_size == 0:
            raise RuntimeError(f"Chart output is empty: {path.name}")
    print(f"Generated {len(outputs)} charts in {CHART_DIR.relative_to(BASE_DIR)}")
    for path in outputs:
        print(f"- {path.name}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
