# StockWise Code Explanation — Simple Walkthrough

This guide explains the purpose and flow of each main project file in simple terms. Read it alongside the source code in `src/`, `app/`, `sql/`, and `notebooks/`.

## 1. Data generator — `src/01_generate_data.py`

### Imports and constants

- `Path` builds file paths safely on Windows, macOS, and Linux.
- `numpy` creates repeatable random values.
- `pandas` stores generated records in DataFrames and writes CSV files.
- `SEED = 42` fixes the random sequence. Running the generator again with the same seed and code gives the same records.
- `BASE_DIR` finds the repository root; `RAW_DIR` points to `data/raw/`.

### `add_controlled_quality_issues()`

1. The function receives the five generated DataFrames.
2. `duplicated` records are added deliberately to four datasets.
3. Missing category, region, reserved quantity, and expected delivery date values are introduced.
4. A negative unit cost and an extreme available quantity are inserted as invalid examples.
5. A movement label with whitespace and a synonym (`issue`) are inserted to test text cleaning.
6. The modified DataFrames are returned. These issues are intentional test data, not accidental corruption.

### `generate_data()`

- `np.random.default_rng(seed)` creates the seeded random generator.
- The Suppliers DataFrame is created first so products can refer to valid supplier IDs.
- The Products DataFrame stores one row per product, including SKU, category, cost, reorder level, and supplier.
- Stock movements are generated for each product across the 90-day period. `IN` adds stock; `OUT` removes stock.
- Inventory snapshots store opening, received, issued, reserved, and available quantities.
- Purchase orders store supplier/product IDs and order, expected-delivery, and actual-delivery dates.
- The five DataFrames are passed to `add_controlled_quality_issues()` and returned.

### `main()`

1. Creates `data/raw/` if it does not exist.
2. Calls `generate_data()`.
3. Writes each DataFrame to its own CSV file.
4. Prints each file's row and column counts.

## 2. Cleaning pipeline — `src/02_clean_data.py`

### Constants

- `DATE_COLUMNS` lists date columns that need consistent parsing.
- `PRIMARY_KEYS` maps each dataset to its unique identifier.
- `RAW_DIR`, `CLEAN_DIR`, and `REPORT_DIR` separate source, cleaned, and report files.

### `add_log()`

Adds a row to the cleaning log only when at least one row was affected. Each log row records the dataset, issue, applied rule, and affected-row count.

### `clean_dataset()`

1. Copies the raw DataFrame so the original input is not changed.
2. Uses `duplicated(keep="first")` to identify exact duplicate rows and keeps the first copy.
3. Trims text fields using `str.strip()`.
4. Standardises category and region labels to title case.
5. Standardises movement labels to uppercase and maps `ISSUE`/`ISSUED` to `OUT`.
6. For Products, missing category becomes `Unclassified`; a negative unit cost is replaced by the median valid cost.
7. For Suppliers, a missing region becomes `Unknown`.
8. For Inventory, missing reserved quantity becomes zero. An extreme available quantity below -1000 is reconstructed from opening + received − issued. Ordinary negative available quantities remain because they can represent stock-outs.
9. For Purchase Orders, a missing expected date is imputed using the median observed expected lead time. Non-positive order quantity is replaced with the median valid quantity.
10. Date columns are parsed. Unparseable dates are logged and retained as missing rather than silently deleting the row.
11. Missing primary keys cause an error; the script does not invent IDs.
12. Numeric columns are converted back to numeric types.
13. The cleaned DataFrame is returned.

### `main()`

Reads each raw CSV, calls `clean_dataset()`, writes the clean CSV to `data/clean/`, and writes the combined log to `reports/cleaning_log.csv`.

## 3. Oracle loader — `src/03_load_sql.py`

- `read_clean()` loads one cleaned CSV and gives a clear error if it is missing.
- `parse_queries()` reads `sql/queries.sql` and splits it into the seven named query sections.
- `date_record()` converts a date to a numeric YYYYMMDD key and creates its year, quarter, month, and weekday attributes.
- `load_data()` inserts Suppliers, Products, and Dates first. It then reads the generated surrogate keys and inserts Inventory, Stock Movement, and Purchase Order facts.
- `executemany()` sends batches of rows to Oracle instead of issuing one insert per row.
- `--replace` deletes project records in foreign-key-safe order before reloading. Use it only in the dedicated StockWise schema.
- `export_query_results()` executes each SQL query and writes the returned rows to `reports/sql_results/`.
- Database credentials are read from environment variables, not hard-coded into the script.

**Important:** the loader code is committed, but actual Oracle execution still requires a configured Oracle database and credentials.

## 4. SQL and PL/SQL

### `sql/schema.sql`

- `CREATE TABLE` defines the three dimensions and three fact tables.
- Primary keys uniquely identify rows.
- Foreign keys connect fact rows to dimensions.
- `CHECK` constraints reject invalid ratings, costs, quantities, or movement labels.
- Indexes support common joins and filters.

### `sql/queries.sql`

Each query answers a business question:
1. Stock status by category.
2. Products at or below reorder level.
3. Inventory value by category.
4. Monthly IN/OUT movement by category.
5. Supplier lead time and delayed orders.
6. Purchase-order quantity and value by supplier/category.
7. Product-level units received, issued, and net movement.

### `sql/procedures.sql`

The stored procedure opens a `SYS_REFCURSOR` containing products whose available quantity is at or below the reorder level. A client can fetch the returned rows.

## 5. Python charts — `src/04_analysis_charts.py`

- Clean CSVs are loaded with Pandas.
- Inventory is joined to Products using `product_id`.
- Stock status is assigned using the documented business rules.
- GroupBy and aggregation calculate category and supplier summaries.
- Matplotlib creates seven PNG charts.
- The estimated stock-out trend rebuilds daily balances from opening quantity and dated movements. It is an estimate, not a measured daily stock history.

## 6. Streamlit dashboard — `app/streamlit_app.py`

- `load_data()` reads the clean CSVs.
- `prepare_frames()` joins product/supplier details and calculates stock status, lead time, and delay flags.
- `apply_filters()` filters inventory, orders, and movements using selected categories, suppliers, and dates.
- `main()` creates the page, sidebar filters, four KPI tiles, three Plotly charts, and a reorder-attention table.
- Streamlit reruns the app when a user changes a filter, so the displayed figures update.

## 7. Excel generator — `src/05_build_excel.py`

- Reads the five clean CSVs.
- Uses Pandas merges to build a product-level stock analysis table.
- Calculates inventory value, stock status, reorder gap, supplier lead time, and delay flags.
- Uses openpyxl to create worksheets, Excel tables, formulas, and charts.
- The Cross_Check sheet contains Python values and blank Oracle values until real SQL results are available.
- The workbook generator creates the file locally at `excel/StockWise_Analysis.xlsx`.

Native Excel PivotTables and slicers are added through Excel Desktop using `excel/Power_Query_Guide.md`.

## 8. Automated tests — `tests/test_pipeline.py`

- Pytest fixtures load the clean CSVs once for the test session.
- Tests check unique primary keys and required identifiers.
- Range tests check costs, reorder levels, ratings, quantities, and movement labels.
- Foreign-key tests confirm that fact records refer to existing product/supplier IDs.
- Date tests check valid dates and chronological order.
- Cleaning-log tests check that corrections are documented.
- The Oracle reconciliation test runs only when actual query-result CSVs exist; otherwise it is marked SKIP, not PASS.
- `tests/run_tests.py` converts pytest results into `reports/test_results.csv`.

## 9. Key Pandas and Python terms

| Term | Simple meaning in StockWise |
|---|---|
| DataFrame | A table of rows and columns |
| `read_csv()` | Reads a CSV file into a DataFrame |
| `to_csv()` | Saves a DataFrame as a CSV file |
| `merge()` | Joins two tables using a common key |
| `groupby()` | Groups rows so they can be summarised |
| `agg()` | Calculates summary values such as sum, count, or mean |
| `isna()` | Finds missing values |
| `duplicated()` | Finds duplicate rows |
| `loc[]` | Selects or updates rows/columns using conditions |
| `np.where()` / `np.select()` | Assigns values based on conditions |
| `Path` | Builds safe file paths |

## 10. Example calculation explained

```python
stock["inventory_value"] = stock["available_quantity"] * stock["unit_cost"]
```

- `stock` is the merged product and inventory table.
- `available_quantity` is the number of units available in the snapshot.
- `unit_cost` is the cost per unit.
- Multiplying the two gives the inventory value for each product row.
- The total inventory value is the sum of that new column.

```python
orders["lead_time_days"] = (
    orders["actual_delivery_date"] - orders["order_date"]
).dt.days
```

- Subtract the order date from the actual delivery date.
- `.dt.days` extracts the number of calendar days.
- The result is the supplier lead time for each order.
