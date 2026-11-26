"""StockWise interactive inventory dashboard.

Run from the repository root:
    streamlit run app/streamlit_app.py

Install project packages first:
    python -m pip install -r requirements.txt
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "clean"


def load_data(clean_dir=CLEAN_DIR):
    required = ["products", "suppliers", "inventory", "purchase_orders", "stock_movements"]
    missing = [name for name in required if not (clean_dir / f"{name}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing clean datasets: {', '.join(missing)}. "
            "Run src/01_generate_data.py and src/02_clean_data.py first."
        )
    products = pd.read_csv(clean_dir / "products.csv")
    suppliers = pd.read_csv(clean_dir / "suppliers.csv")
    inventory = pd.read_csv(clean_dir / "inventory.csv")
    orders = pd.read_csv(
        clean_dir / "purchase_orders.csv",
        parse_dates=["order_date", "expected_delivery_date", "actual_delivery_date"],
    )
    movements = pd.read_csv(
        clean_dir / "stock_movements.csv",
        parse_dates=["movement_date"],
    )
    return products, suppliers, inventory, orders, movements


def prepare_frames(products, suppliers, inventory, orders, movements):
    stock = inventory.merge(products, on="product_id", how="left", validate="one_to_one")
    stock = stock.merge(
        suppliers[["supplier_id", "supplier_name"]],
        on="supplier_id", how="left", validate="many_to_one"
    )
    stock["inventory_value"] = stock["available_quantity"] * stock["unit_cost"]
    stock["stock_status"] = "Healthy"
    stock.loc[
        (stock["available_quantity"] > 0)
        & (stock["available_quantity"] <= stock["reorder_level"]),
        "stock_status",
    ] = "Low stock"
    stock.loc[stock["available_quantity"] <= 0, "stock_status"] = "Stock-out"

    order_view = orders.merge(
        products[["product_id", "category"]],
        on="product_id", how="left", validate="many_to_one"
    )
    order_view["lead_time_days"] = (
        order_view["actual_delivery_date"] - order_view["order_date"]
    ).dt.days
    order_view["is_delayed"] = (
        order_view["actual_delivery_date"] > order_view["expected_delivery_date"]
    )

    movement_view = movements.merge(
        products[["product_id", "category", "supplier_id"]],
        on="product_id", how="left", validate="many_to_one"
    )
    movement_view["month"] = movement_view["movement_date"].dt.to_period("M").astype(str)
    return stock, order_view, movement_view


def apply_filters(stock, orders, movements, categories, supplier_ids, start_date, end_date):
    selected_stock = stock[
        stock["category"].isin(categories)
        & stock["supplier_id"].isin(supplier_ids)
    ].copy()
    selected_orders = orders[
        orders["category"].isin(categories)
        & orders["supplier_id"].isin(supplier_ids)
        & orders["order_date"].dt.date.between(start_date, end_date)
    ].copy()
    selected_movements = movements[
        movements["category"].isin(categories)
        & movements["supplier_id"].isin(supplier_ids)
        & movements["movement_date"].dt.date.between(start_date, end_date)
    ].copy()
    return selected_stock, selected_orders, selected_movements


def main():
    import streamlit as st
    import plotly.express as px

    st.set_page_config(page_title="StockWise | Inventory Analytics",
                       page_icon="📦", layout="wide")
    st.title("StockWise")
    st.caption("Inventory and Stock-Out Analysis | Synthetic teaching dataset")

    try:
        products, suppliers, inventory, orders, movements = load_data()
        stock, order_view, movement_view = prepare_frames(
            products, suppliers, inventory, orders, movements
        )
    except (FileNotFoundError, KeyError, ValueError) as error:
        st.error(str(error))
        st.info("From the repository root, run the data generator and cleaning script first.")
        st.stop()

    categories = sorted(stock["category"].dropna().unique().tolist())
    supplier_options = suppliers[["supplier_id", "supplier_name"]].sort_values("supplier_name")
    supplier_labels = dict(zip(
        supplier_options["supplier_id"], supplier_options["supplier_name"]
    ))
    min_date = min(movement_view["movement_date"].min().date(),
                   order_view["order_date"].min().date())
    max_date = max(movement_view["movement_date"].max().date(),
                   order_view["order_date"].max().date())

    st.sidebar.header("Dashboard filters")
    selected_categories = st.sidebar.multiselect(
        "Product category", categories, default=categories
    )
    selected_suppliers = st.sidebar.multiselect(
        "Supplier", supplier_options["supplier_id"].tolist(),
        default=supplier_options["supplier_id"].tolist(),
        format_func=lambda value: supplier_labels.get(value, value),
    )
    selected_dates = st.sidebar.date_input(
        "Activity date range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date = end_date = selected_dates

    filtered_stock, filtered_orders, filtered_movements = apply_filters(
        stock, order_view, movement_view,
        selected_categories, selected_suppliers, start_date, end_date
    )
    stockouts = int((filtered_stock["stock_status"] == "Stock-out").sum())
    available_units = int(filtered_stock["available_quantity"].sum())
    inventory_value = float(filtered_stock["inventory_value"].sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Products in view", f"{filtered_stock['product_id'].nunique():,}")
    k2.metric("Available units", f"{available_units:,}")
    k3.metric("Stock-out products", f"{stockouts:,}")
    k4.metric("Inventory value", f"{inventory_value:,.2f}")

    st.subheader("Inventory status")
    if filtered_stock.empty:
        st.info("No inventory rows match the selected filters.")
    else:
        status_summary = (
            filtered_stock.groupby(["category", "stock_status"])
            .size().reset_index(name="product_count")
        )
        fig_status = px.bar(
            status_summary, x="category", y="product_count",
            color="stock_status", barmode="stack",
            title="Product Stock Status by Category",
            labels={"category": "Category", "product_count": "Products",
                    "stock_status": "Stock status"},
        )
        st.plotly_chart(fig_status, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Stock movement trend")
        if filtered_movements.empty:
            st.info("No stock movements match the selected filters and dates.")
        else:
            monthly = (
                filtered_movements.groupby(["month", "movement_type"], as_index=False)
                ["quantity"].sum()
            )
            fig_moves = px.line(
                monthly, x="month", y="quantity", color="movement_type",
                markers=True, title="Monthly IN and OUT Quantities",
                labels={"month": "Month", "quantity": "Units moved",
                        "movement_type": "Movement"},
            )
            st.plotly_chart(fig_moves, use_container_width=True)

    with right:
        st.subheader("Supplier performance")
        if filtered_orders.empty:
            st.info("No purchase orders match the selected filters and dates.")
        else:
            supplier_perf = (
                filtered_orders.groupby("supplier_id", as_index=False)
                .agg(
                    average_lead_time=("lead_time_days", "mean"),
                    delayed_orders=("is_delayed", "sum"),
                )
                .merge(suppliers[["supplier_id", "supplier_name"]],
                       on="supplier_id", how="left")
                .sort_values("average_lead_time")
            )
            fig_supplier = px.bar(
                supplier_perf, x="average_lead_time", y="supplier_name",
                orientation="h", title="Average Supplier Lead Time",
                labels={"average_lead_time": "Calendar days",
                        "supplier_name": "Supplier"},
                hover_data=["delayed_orders"],
            )
            st.plotly_chart(fig_supplier, use_container_width=True)

    st.subheader("Reorder attention")
    if not filtered_stock.empty:
        attention = filtered_stock[
            filtered_stock["stock_status"].isin(["Stock-out", "Low stock"])
        ].copy()
        attention["reorder_gap"] = (
            attention["reorder_level"] - attention["available_quantity"]
        )
        attention = attention.sort_values("reorder_gap", ascending=False)
        st.dataframe(
            attention[[
                "product_id", "product_name", "category", "supplier_name",
                "available_quantity", "reorder_level", "stock_status", "reorder_gap"
            ]],
            use_container_width=True, hide_index=True,
        )
    st.caption(
        "Source: reproducible synthetic CSV data generated by src/01_generate_data.py. "
        "The activity date filter applies to purchase orders and stock movements; "
        "inventory KPIs use the available inventory snapshot."
    )


if __name__ == "__main__":
    main()
