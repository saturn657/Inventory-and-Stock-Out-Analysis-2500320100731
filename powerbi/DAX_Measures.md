# StockWise Power BI — DAX Measures

Create each measure through **Modeling → New measure**. These measures assume the table and column names from `PowerBI_Data_Model.md`.

| Measure | DAX | Explanation |
|---|---|---|
| Total Products | `Total Products = DISTINCTCOUNT(Products[product_id])` | Counts unique products in the current filter context. |
| Available Units | `Available Units = SUM(Inventory[available_quantity])` | Adds available stock quantities in the selected inventory context. |
| Stock-Out Products | `Stock-Out Products = CALCULATE(DISTINCTCOUNT(Inventory[product_id]), Inventory[available_quantity] <= 0)` | Counts products with zero or negative available stock. |
| Low-Stock Products | `Low-Stock Products = CALCULATE(DISTINCTCOUNT(Inventory[product_id]), FILTER(Inventory, Inventory[available_quantity] > 0 && Inventory[available_quantity] <= RELATED(Products[reorder_level])))` | Counts products above zero but at or below their reorder level. |
| Inventory Value | `Inventory Value = SUMX(Inventory, Inventory[available_quantity] * RELATED(Products[unit_cost]))` | Calculates available quantity multiplied by unit cost for each inventory row, then sums it. |
| Stock-Out Rate | `Stock-Out Rate = DIVIDE([Stock-Out Products], [Total Products], 0)` | Shows the share of products currently in stock-out status. Format as Percentage. |
| Received Units | `Received Units = CALCULATE(SUM(Stock_Movements[quantity]), Stock_Movements[movement_type] = "IN")` | Sums quantities entering inventory. |
| Issued Units | `Issued Units = CALCULATE(SUM(Stock_Movements[quantity]), Stock_Movements[movement_type] = "OUT")` | Sums quantities leaving inventory. |
| Net Movement | `Net Movement = [Received Units] - [Issued Units]` | Shows incoming units minus outgoing units. |
| Purchase Order Lines | `Purchase Order Lines = COUNTROWS(Purchase_Orders)` | Counts purchase-order records in the current context. |
| Units Ordered | `Units Ordered = SUM(Purchase_Orders[quantity_ordered])` | Sums units requested on purchase orders. |
| Ordered Value | `Ordered Value = SUMX(Purchase_Orders, Purchase_Orders[quantity_ordered] * Purchase_Orders[unit_cost])` | Calculates the recorded value of ordered units. |
| Average Lead Time (Days) | `Average Lead Time (Days) = AVERAGEX(FILTER(Purchase_Orders, NOT ISBLANK(Purchase_Orders[actual_delivery_date])), DATEDIFF(Purchase_Orders[order_date], Purchase_Orders[actual_delivery_date], DAY))` | Averages calendar days from order to actual delivery. |
| Delayed Orders | `Delayed Orders = CALCULATE(COUNTROWS(Purchase_Orders), FILTER(Purchase_Orders, NOT ISBLANK(Purchase_Orders[actual_delivery_date]) && Purchase_Orders[actual_delivery_date] > Purchase_Orders[expected_delivery_date]))` | Counts delivered orders whose actual date is later than expected. |
| Orders by Actual Delivery Date | `Orders by Actual Delivery Date = CALCULATE([Purchase Order Lines], USERELATIONSHIP(DimDate[Date], Purchase_Orders[actual_delivery_date]))` | Uses the inactive actual-delivery date relationship for time-based analysis. |
| Orders by Expected Delivery Date | `Orders by Expected Delivery Date = CALCULATE([Purchase Order Lines], USERELATIONSHIP(DimDate[Date], Purchase_Orders[expected_delivery_date]))` | Uses the inactive expected-delivery date relationship. |

## Formatting

- Inventory Value and Ordered Value: Currency or Decimal Number with two decimal places. The synthetic dataset does not specify a real-world currency.
- Stock-Out Rate: Percentage with one or two decimal places.
- Average Lead Time (Days): Decimal Number with one decimal place.
- Counts and quantities: Whole Number.

## Important modelling notes

- The inventory table contains one snapshot date in the generated dataset. Inventory KPIs therefore describe that snapshot, not a historical daily series.
- The date slicer filters movement and purchase-order activity. The Inventory snapshot relationship filters inventory only when the selected date includes its snapshot date.
- Supplier slicers from the Suppliers dimension apply to purchase orders. For inventory and stock movement visuals, use the supplier attributes merged into Products in Power Query.
- Negative available quantity is retained in Inventory Value because the project definition uses available quantity multiplied by unit cost. Interpret negative values as a data signal requiring review, not as physical negative stock value.
