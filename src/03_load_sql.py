"""Load StockWise clean CSV files into Oracle and export seven SQL query results.

Setup:
    python -m pip install -r requirements.txt

Set STOCKWISE_ORACLE_USER, STOCKWISE_ORACLE_PASSWORD, and STOCKWISE_ORACLE_DSN.
Then run:
    python src/03_load_sql.py --replace

Use --skip-load to run the seven queries against an already-loaded schema.
The --replace option deletes project rows in dependency order before reloading.
"""
from pathlib import Path
import argparse
import os
import re
import sys
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "clean"
QUERY_FILE = BASE_DIR / "sql" / "queries.sql"
OUTPUT_DIR = BASE_DIR / "reports" / "sql_results"


def read_clean(name):
    path = CLEAN_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run src/01_generate_data.py and src/02_clean_data.py first.")
    return pd.read_csv(path)


def parse_queries(sql_text):
    sections = re.split(r"(?m)^-- (Q\d+:.*?)\s*$", sql_text)
    queries = []
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        statement = sections[i + 1]
        statement = "\n".join(line for line in statement.splitlines()
                               if not line.strip().startswith("--")).strip()
        statement = statement.rstrip().removesuffix(";").strip()
        if statement:
            queries.append((title, statement))
    if len(queries) != 7:
        raise ValueError(f"Expected exactly 7 SQL queries, found {len(queries)}.")
    return queries


def date_record(value):
    dt = pd.to_datetime(value).date()
    key = int(dt.strftime("%Y%m%d"))
    quarter = (dt.month - 1) // 3 + 1
    return (key, dt, dt.year, quarter, dt.month, dt.strftime("%B"),
            dt.day, dt.strftime("%A"))


def load_data(connection, replace=False):
    suppliers = read_clean("suppliers")
    products = read_clean("products")
    inventory = read_clean("inventory")
    purchase_orders = read_clean("purchase_orders")
    movements = read_clean("stock_movements")

    with connection.cursor() as cursor:
        if replace:
            for table in ("fact_purchase_order", "fact_stock_movement",
                          "fact_inventory", "dim_product", "dim_supplier", "dim_date"):
                cursor.execute(f"DELETE FROM {table}")

        cursor.executemany(
            """INSERT INTO dim_supplier
               (supplier_id, supplier_name, region, rating)
               VALUES (:1, :2, :3, :4)""",
            list(suppliers[["supplier_id", "supplier_name", "region", "rating"]]
                 .itertuples(index=False, name=None))
        )
        cursor.executemany(
            """INSERT INTO dim_product
               (product_id, sku, product_name, category, unit_cost, reorder_level)
               VALUES (:1, :2, :3, :4, :5, :6)""",
            list(products[["product_id", "sku", "product_name", "category", "unit_cost", "reorder_level"]]
                 .itertuples(index=False, name=None))
        )

        date_values = set(inventory["snapshot_date"].dropna().tolist())
        date_values.update(movements["movement_date"].dropna().tolist())
        for col in ("order_date", "expected_delivery_date", "actual_delivery_date"):
            date_values.update(purchase_orders[col].dropna().tolist())
        date_rows = [date_record(value) for value in sorted(date_values)]
        cursor.executemany(
            """INSERT INTO dim_date
               (date_key, full_date, calendar_year, calendar_quarter,
                calendar_month, month_name, day_of_month, weekday_name)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
            date_rows
        )

        cursor.execute("SELECT product_id, product_key FROM dim_product")
        product_keys = {natural: surrogate for natural, surrogate in cursor.fetchall()}
        cursor.execute("SELECT supplier_id, supplier_key FROM dim_supplier")
        supplier_keys = {natural: surrogate for natural, surrogate in cursor.fetchall()}

        inv_rows = [
            (r.inventory_id, product_keys[r.product_id], date_record(r.snapshot_date)[0],
             int(r.opening_quantity), int(r.received_quantity), int(r.issued_quantity),
             int(r.reserved_quantity), int(r.available_quantity))
            for r in inventory.itertuples(index=False)
        ]
        cursor.executemany(
            """INSERT INTO fact_inventory
               (inventory_id, product_key, snapshot_date_key, opening_quantity,
                received_quantity, issued_quantity, reserved_quantity, available_quantity)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
            inv_rows
        )

        movement_rows = [
            (r.movement_id, product_keys[r.product_id], date_record(r.movement_date)[0],
             r.movement_type, int(r.quantity), r.reference)
            for r in movements.itertuples(index=False)
        ]
        cursor.executemany(
            """INSERT INTO fact_stock_movement
               (movement_id, product_key, movement_date_key, movement_type, quantity, reference)
               VALUES (:1, :2, :3, :4, :5, :6)""",
            movement_rows
        )

        po_rows = [
            (r.order_id, product_keys[r.product_id], supplier_keys[r.supplier_id],
             date_record(r.order_date)[0], date_record(r.expected_delivery_date)[0],
             date_record(r.actual_delivery_date)[0] if pd.notna(r.actual_delivery_date) else None,
             int(r.quantity_ordered), float(r.unit_cost))
            for r in purchase_orders.itertuples(index=False)
        ]
        cursor.executemany(
            """INSERT INTO fact_purchase_order
               (order_id, product_key, supplier_key, order_date_key,
                expected_delivery_date_key, actual_delivery_date_key,
                quantity_ordered, unit_cost)
               VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""",
            po_rows
        )
    connection.commit()
    print("Loaded dimensions and fact tables successfully.")


def export_query_results(connection):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    queries = parse_queries(QUERY_FILE.read_text(encoding="utf-8"))
    with connection.cursor() as cursor:
        for title, statement in queries:
            cursor.execute(statement)
            columns = [item[0].lower() for item in cursor.description]
            rows = cursor.fetchall()
            frame = pd.DataFrame(rows, columns=columns)
            filename = title.split(":", 1)[0].replace(" ", "_") + "_" + re.sub(
                r"[^a-z0-9]+", "_", title.split(":", 1)[1].lower()
            ).strip("_") + ".csv"
            frame.to_csv(OUTPUT_DIR / filename, index=False)
            print(f"Exported {filename}: {len(frame)} rows")


def main():
    parser = argparse.ArgumentParser(description="Load StockWise into Oracle and run seven SQL reports.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--replace", action="store_true",
                       help="Delete existing StockWise rows before loading clean CSVs.")
    group.add_argument("--skip-load", action="store_true",
                       help="Skip CSV loading and run queries against existing tables.")
    args = parser.parse_args()

    user = os.getenv("STOCKWISE_ORACLE_USER")
    password = os.getenv("STOCKWISE_ORACLE_PASSWORD")
    dsn = os.getenv("STOCKWISE_ORACLE_DSN")
    if not all((user, password, dsn)):
        sys.exit("Set STOCKWISE_ORACLE_USER, STOCKWISE_ORACLE_PASSWORD, and STOCKWISE_ORACLE_DSN first.")

    try:
        import oracledb
    except ImportError:
        sys.exit("Oracle driver missing. Run: python -m pip install -r requirements.txt")

    with oracledb.connect(user=user, password=password, dsn=dsn) as connection:
        if not args.skip_load:
            load_data(connection, replace=args.replace)
        export_query_results(connection)


if __name__ == "__main__":
    main()
