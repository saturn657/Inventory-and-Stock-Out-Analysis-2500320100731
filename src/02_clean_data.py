"""Clean StockWise raw CSV files and write a transparent quality log.

Run from the repository root:
    python src/02_clean_data.py

Raw files are never overwritten. Cleaned files go to data/clean/ and the
row-level issue summary goes to reports/cleaning_log.csv.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
REPORT_DIR = BASE_DIR / "reports"

DATE_COLUMNS = {
    "inventory": ["snapshot_date"],
    "purchase_orders": ["order_date", "expected_delivery_date", "actual_delivery_date"],
    "stock_movements": ["movement_date"],
}
PRIMARY_KEYS = {
    "products": "product_id",
    "suppliers": "supplier_id",
    "inventory": "inventory_id",
    "purchase_orders": "order_id",
    "stock_movements": "movement_id",
}


def add_log(logs, dataset, issue, rule, rows):
    if rows:
        logs.append({
            "dataset": dataset,
            "issue": issue,
            "rule_applied": rule,
            "rows_affected": int(rows),
        })


def clean_dataset(name, frame, logs):
    df = frame.copy()
    initial_rows = len(df)

    duplicate_mask = df.duplicated(keep="first")
    add_log(logs, name, "Exact duplicate rows",
            "Keep the first identical record and remove subsequent copies.",
            duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    for col in df.select_dtypes(include="object").columns:
        before = df[col].copy()
        df[col] = df[col].astype("string").str.strip()
        changed = (before.fillna("").astype(str) != df[col].fillna("").astype(str)).sum()
        add_log(logs, name, f"Inconsistent whitespace in {col}",
                "Trim leading and trailing whitespace.", changed)
        if col in {"category", "region", "movement_type"}:
            if col == "movement_type":
                normalised = df[col].str.upper()
                synonym_mask = normalised.isin(["ISSUE", "ISSUED"])
                add_log(
                    logs, name, "Non-standard movement_type synonym",
                    "Map ISSUE/ISSUED to OUT; retain IN and OUT as the only standard labels.",
                    synonym_mask.sum()
                )
                normalised = normalised.replace({"ISSUE": "OUT", "ISSUED": "OUT"})
            else:
                normalised = df[col].str.title()
            changed = (df[col].fillna("") != normalised.fillna("")).sum()
            add_log(logs, name, f"Inconsistent label case in {col}",
                    "Standardise labels to uppercase for movement_type and title case otherwise.",
                    changed)
            df[col] = normalised

    if name == "products":
        missing = df["category"].isna() | df["category"].eq("")
        add_log(logs, name, "Missing category",
                "Replace missing category with 'Unclassified'.", missing.sum())
        df.loc[missing, "category"] = "Unclassified"

        invalid = pd.to_numeric(df["unit_cost"], errors="coerce").lt(0)
        median_cost = pd.to_numeric(df.loc[~invalid, "unit_cost"], errors="coerce").median()
        add_log(logs, name, "Negative unit_cost",
                "Replace negative unit_cost with the median valid product unit_cost.",
                invalid.sum())
        df.loc[invalid, "unit_cost"] = median_cost

        invalid_reorder = pd.to_numeric(df["reorder_level"], errors="coerce").lt(0)
        median_reorder = int(round(pd.to_numeric(
            df.loc[~invalid_reorder, "reorder_level"], errors="coerce"
        ).median()))
        add_log(logs, name, "Negative reorder_level",
                "Replace negative reorder_level with the median valid reorder level.",
                invalid_reorder.sum())
        df.loc[invalid_reorder, "reorder_level"] = median_reorder

    elif name == "suppliers":
        missing = df["region"].isna() | df["region"].eq("")
        add_log(logs, name, "Missing region",
                "Replace missing region with 'Unknown'.", missing.sum())
        df.loc[missing, "region"] = "Unknown"

    elif name == "inventory":
        missing = df["reserved_quantity"].isna()
        add_log(logs, name, "Missing reserved_quantity",
                "Fill missing reserved_quantity with 0 and record the correction.",
                missing.sum())
        df.loc[missing, "reserved_quantity"] = 0

        extreme = pd.to_numeric(df["available_quantity"], errors="coerce").lt(-1000)
        reconstructed = (pd.to_numeric(df["opening_quantity"], errors="coerce")
                         + pd.to_numeric(df["received_quantity"], errors="coerce")
                         - pd.to_numeric(df["issued_quantity"], errors="coerce"))
        add_log(logs, name, "Implausible available_quantity below -1000",
                "Recalculate from opening_quantity + received_quantity - issued_quantity.",
                extreme.sum())
        df.loc[extreme, "available_quantity"] = reconstructed.loc[extreme]

    elif name == "purchase_orders":
        expected_missing = (df["expected_delivery_date"].isna()
                            | df["expected_delivery_date"].eq(""))
        valid_order_dates = pd.to_datetime(df["order_date"], errors="coerce")
        valid_expected = pd.to_datetime(
            df.loc[~expected_missing, "expected_delivery_date"], errors="coerce"
        )
        lead_days = (valid_expected - valid_order_dates.loc[~expected_missing]).dt.days
        median_lead = max(1, int(lead_days.dropna().median())) if lead_days.notna().any() else 7
        add_log(logs, name, "Missing expected_delivery_date",
                f"Impute order_date + median observed expected lead time ({median_lead} days).",
                expected_missing.sum())
        df.loc[expected_missing, "expected_delivery_date"] = (
            valid_order_dates.loc[expected_missing] + pd.to_timedelta(median_lead, unit="D")
        ).dt.strftime("%Y-%m-%d")

        negative_qty = pd.to_numeric(df["quantity_ordered"], errors="coerce").le(0)
        add_log(logs, name, "Non-positive quantity_ordered",
                "Replace non-positive quantity with the median positive order quantity.",
                negative_qty.sum())
        if negative_qty.any():
            median_qty = pd.to_numeric(df.loc[~negative_qty, "quantity_ordered"]).median()
            df.loc[negative_qty, "quantity_ordered"] = median_qty

    for col in DATE_COLUMNS.get(name, []):
        parsed = pd.to_datetime(df[col], errors="coerce")
        invalid = parsed.isna()
        add_log(logs, name, f"Invalid or missing date in {col}",
                "Retain as missing for explicit review; do not silently drop the row.",
                invalid.sum())
        df[col] = parsed.dt.strftime("%Y-%m-%d")

    key = PRIMARY_KEYS[name]
    missing_key = df[key].isna() | df[key].astype("string").str.strip().eq("")
    if missing_key.any():
        raise ValueError(f"{name}: {int(missing_key.sum())} rows have missing {key}; no IDs were fabricated.")

    for col in df.columns:
        if col in {"unit_cost", "rating"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif col in {"reorder_level", "opening_quantity", "received_quantity",
                     "issued_quantity", "reserved_quantity", "available_quantity",
                     "quantity_ordered", "quantity"}:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    if len(df) > initial_rows:
        raise AssertionError(f"{name}: cleaning unexpectedly increased row count.")
    return df


def main():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    logs = []
    for name in PRIMARY_KEYS:
        path = RAW_DIR / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run 'python src/01_generate_data.py' first."
            )
        raw = pd.read_csv(path)
        clean = clean_dataset(name, raw, logs)
        clean.to_csv(CLEAN_DIR / f"{name}.csv", index=False)
        print(f"{name}: {len(raw):,} raw rows -> {len(clean):,} clean rows")

    log_df = pd.DataFrame(logs, columns=[
        "dataset", "issue", "rule_applied", "rows_affected"
    ])
    log_path = REPORT_DIR / "cleaning_log.csv"
    log_df.to_csv(log_path, index=False)
    print(f"Cleaning log: {log_path.relative_to(BASE_DIR)} ({len(log_df)} issue entries)")
    print("Cleaning complete. Raw files were not modified.")


if __name__ == "__main__":
    main()
