# StockWise Excel — Power Query, PivotTables and Slicers

This guide explains how to reproduce the cleaning and reporting steps in Excel. The Python-cleaned CSVs remain the reference dataset; the Excel workbook is a second analysis and reconciliation surface.

## 1. Import the CSVs with Power Query

1. Open Excel and create a blank workbook.
2. Select **Data → Get Data → From File → From Text/CSV**.
3. Import each file from `data/clean/`: products.csv, suppliers.csv, inventory.csv, purchase_orders.csv, and stock_movements.csv.
4. Choose **Transform Data** rather than Load.
5. In Power Query, rename the queries to Products, Suppliers, Inventory, Purchase_Orders, and Stock_Movements.
6. Set IDs and labels to Text; quantity fields to Whole Number; cost/rating fields to Decimal Number; and date fields to Date.
7. For text columns, select **Transform → Format → Trim**, then **Clean** where appropriate.
8. Standardise category and region labels with **Transform → Format → Capitalize Each Word**. Standardise movement_type to uppercase.
9. Replace missing Products[category] with `Unclassified`.
10. Replace missing Suppliers[region] with `Unknown`.
11. Replace missing Inventory[reserved_quantity] with 0.
12. Filter Products[unit_cost] to identify negative values; replace invalid negative values with the median of valid costs (the Python reference uses the median valid product cost).
13. In Inventory, flag available_quantity values below -1000 and reconstruct them as opening_quantity + received_quantity - issued_quantity. Keep ordinary negative quantities because they can represent stock-outs.
14. In Purchase_Orders, fill missing expected_delivery_date with order_date plus the median observed expected lead time. Keep a note of the imputation rule.
15. Select **Home → Close & Load To… → Table** and load each query to a worksheet.

Do not silently remove records. Record each change and affected-row count in the cleaning log. The reference log is `reports/cleaning_log.csv`.

## 2. Create PivotTables

Use the loaded Excel tables:

### Inventory by category
1. Select a cell in Stock_Analysis.
2. Choose **Insert → PivotTable → From Table/Range**.
3. Put category in Rows.
4. Put available_quantity in Values (Sum).
5. Add stock_status to Columns and product_id to Values (Distinct Count, if the Data Model is enabled; otherwise use Count after confirming one row per product).

### Supplier performance
1. Insert a PivotTable from Purchase_Orders.
2. Put supplier_name in Rows.
3. Put lead_time_days in Values and change the aggregation to Average.
4. Put is_delayed in Filters or Columns and order_id in Values (Count).
5. Add quantity_ordered to Values (Sum) if order volume is required.

### Monthly movement
1. Insert a PivotTable from Stock_Movements.
2. Put movement_date in Rows and group by Months and Years.
3. Put movement_type in Columns.
4. Put quantity in Values (Sum).

## 3. Add dashboard slicers

1. Select a PivotTable.
2. Choose **PivotTable Analyze → Insert Slicer**.
3. Add Category, Stock Status, and Supplier fields where available.
4. Add a Date Timeline for movement_date or order_date.
5. Select a slicer, choose **Slicer → Report Connections**, and connect it to the PivotTables that should respond.
6. Arrange slicers at the top or left of the Dashboard sheet and keep labels visible.
7. Test each slicer and clear selections to confirm the dashboard returns to the full dataset.

The generated workbook includes formula-based summary tables and charts. Native Excel PivotTables, slicers, and timelines must be created in Excel Desktop using these steps.

## 4. Formula cross-check

The generated workbook includes a Cross_Check sheet:
- Python values are populated from the cleaned CSVs.
- Oracle SQL values are deliberately blank until the seven Oracle queries have actually been executed.
- Status remains PENDING until an Oracle value is entered; it changes to PASS or FAIL based on the comparison formula.

Do not type estimated SQL values. Use the CSV exports created by `python src/03_load_sql.py --skip-load` after Oracle has been loaded.

## 5. Regenerate the workbook

From the repository root:

```bash
python -m pip install -r requirements.txt
python src/01_generate_data.py
python src/02_clean_data.py
python src/05_build_excel.py
```

The output is `excel/StockWise_Analysis.xlsx`. The workbook contains source data sheets, formula-based category and supplier summaries, a dashboard with charts, and a cross-check sheet.
