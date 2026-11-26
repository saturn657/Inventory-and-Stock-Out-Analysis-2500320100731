# StockWise Power BI — Data Model Setup

This guide builds the Power BI data model from the cleaned CSV files. The source data is synthetic teaching data.

## 1. Prepare the source files

From the repository root, run:

```bash
python -m pip install -r requirements.txt
python src/01_generate_data.py
python src/02_clean_data.py
```

The CSVs used by Power BI are in `data/clean/`:
- products.csv
- suppliers.csv
- inventory.csv
- purchase_orders.csv
- stock_movements.csv

## 2. Import the CSV files

1. Open **Power BI Desktop**.
2. Select **Home → Get data → Text/CSV**.
3. Browse to `data/clean/products.csv`, select it, and choose **Transform Data**.
4. In Power Query, rename the query to `Products`.
5. Repeat for `suppliers.csv`, `inventory.csv`, `purchase_orders.csv`, and `stock_movements.csv`; name the queries `Suppliers`, `Inventory`, `Purchase_Orders`, and `Stock_Movements`.
6. Confirm data types:
   - IDs and labels: Text.
   - Quantity and reorder fields: Whole Number.
   - Unit cost: Decimal Number or Fixed Decimal Number.
   - Dates: Date.
7. For `Purchase_Orders`, set `order_date`, `expected_delivery_date`, and `actual_delivery_date` to Date.
8. For `Stock_Movements`, set `movement_date` to Date.
9. Select **Close & Apply**.

## 3. Add supplier descriptions to Products

The source Products table contains the primary supplier ID for each product. To make supplier filtering work for inventory and movement visuals without creating ambiguous relationship paths:

1. Select **Transform Data**.
2. Select the `Products` query.
3. Choose **Home → Merge Queries**.
4. Merge `Products` with `Suppliers` using `supplier_id` in both tables.
5. Select **Left Outer (all from first, matching from second)**.
6. Expand the merged column and select `supplier_name` and `region`; clear the prefix option if desired.
7. Keep the original `Suppliers` table as a separate dimension for purchase-order supplier analysis.
8. Select **Close & Apply**.

Do not create a relationship from `Suppliers` to `Products` after this merge. Supplier attributes used for product/inventory/movement visuals are now part of Products; the Suppliers dimension is used for the supplier recorded on each purchase order.

## 4. Create the date table

In Power BI Desktop, select **Modeling → New table** and enter:

```DAX
DimDate =
VAR AllDates =
    UNION(
        SELECTCOLUMNS(Inventory, "DateValue", Inventory[snapshot_date]),
        SELECTCOLUMNS(Stock_Movements, "DateValue", Stock_Movements[movement_date]),
        SELECTCOLUMNS(Purchase_Orders, "DateValue", Purchase_Orders[order_date]),
        SELECTCOLUMNS(Purchase_Orders, "DateValue", Purchase_Orders[expected_delivery_date]),
        SELECTCOLUMNS(Purchase_Orders, "DateValue", Purchase_Orders[actual_delivery_date])
    )
VAR MinDate = MINX(AllDates, [DateValue])
VAR MaxDate = MAXX(AllDates, [DateValue])
RETURN
    ADDCOLUMNS(
        CALENDAR(MinDate, MaxDate),
        "DateKey", YEAR([Date]) * 10000 + MONTH([Date]) * 100 + DAY([Date]),
        "Year", YEAR([Date]),
        "Quarter", "Q" & FORMAT([Date], "Q"),
        "MonthNumber", MONTH([Date]),
        "Month", FORMAT([Date], "MMM"),
        "YearMonth", FORMAT([Date], "YYYY-MM"),
        "Day", DAY([Date]),
        "Weekday", FORMAT([Date], "DDD")
    )
```

Then:
1. Select the `DimDate` table.
2. Choose **Table tools → Mark as date table → Date**.
3. Sort `DimDate[Month]` by `DimDate[MonthNumber]`.
4. Sort `DimDate[YearMonth]` by a numeric YearMonth sort key if you add one; otherwise use the Date field for chronological axes.

## 5. Create relationships

Open **Model view**. Create these relationships by dragging the one-side key to the many-side foreign key.

| One-side table/column | Many-side table/column | Cardinality | Cross-filter |
|---|---|---|---|
| Products[product_id] | Inventory[product_id] | One-to-many (1:*) | Single |
| Products[product_id] | Stock_Movements[product_id] | One-to-many (1:*) | Single |
| Products[product_id] | Purchase_Orders[product_id] | One-to-many (1:*) | Single |
| Suppliers[supplier_id] | Purchase_Orders[supplier_id] | One-to-many (1:*) | Single |
| DimDate[Date] | Inventory[snapshot_date] | One-to-many (1:*) | Single |
| DimDate[Date] | Stock_Movements[movement_date] | One-to-many (1:*) | Single |
| DimDate[Date] | Purchase_Orders[order_date] | One-to-many (1:*) | Single, active |

Create two additional relationships from DimDate to Purchase_Orders:
- DimDate[Date] → Purchase_Orders[expected_delivery_date] (inactive).
- DimDate[Date] → Purchase_Orders[actual_delivery_date] (inactive).

Power BI allows only one active relationship between the same tables. Use `USERELATIONSHIP` in measures when analysing expected or actual delivery dates. Keep all relationships single-direction from dimensions to facts; avoid bidirectional filtering.

## 6. Add calculated columns only when needed

Prefer measures for aggregated KPIs. If a readable status column is useful in a product table, create it in Inventory:

```DAX
Stock Status =
VAR Available = Inventory[available_quantity]
VAR Reorder = RELATED(Products[reorder_level])
RETURN
    SWITCH(
        TRUE(),
        Available <= 0, "Stock-out",
        Available <= Reorder, "Low stock",
        "Healthy"
    )
```

## 7. Add the measures

Create the measures listed in `DAX_Measures.md` using **Modeling → New measure**. Keep the measures in a dedicated measure table if desired.

## 8. Validate the model

- Confirm every dimension key is unique.
- Confirm each fact foreign key matches a dimension key.
- Check that relationships show 1 on the dimension side and * on the fact side.
- Confirm the date table covers the earliest and latest dates in all five date columns.
- Compare Total Products, Available Units, Stock-Out Products, and Inventory Value against Python outputs from the cleaned CSVs.
- Verify supplier lead-time and delayed-order totals against the Python analysis.
- If totals differ, check filter direction, date relationships, duplicate rows, and numeric data types before building report visuals.

## 9. Refresh

When the synthetic data is regenerated or cleaned again, use **Home → Refresh** in Power BI Desktop. If file locations change, update the CSV source paths in Power Query.
