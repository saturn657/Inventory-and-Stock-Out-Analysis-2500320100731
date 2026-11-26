# Additional DAX Measures for the Three-Page Report

Add these measures alongside the core measures in `DAX_Measures.md`.

```DAX
Product Inventory Value =
SUMX(
    Inventory,
    Inventory[available_quantity] * RELATED(Products[unit_cost])
)
```
*Calculates inventory value at product grain; use Products[product_name] on the chart axis.*

```DAX
Reorder Gap =
SUMX(
    Inventory,
    RELATED(Products[reorder_level]) - Inventory[available_quantity]
)
```
*Shows reorder threshold minus available quantity; positive values indicate a gap to review.*

```DAX
At-Risk Products =
[Stock-Out Products] + [Low-Stock Products]
```
*Combines stock-out and low-stock product counts.*

```DAX
Delayed Order Rate =
DIVIDE([Delayed Orders], [Purchase Order Lines], 0)
```
*Shows the share of purchase-order rows delivered after the expected date; format as Percentage.*

```DAX
Order Quantity by Actual Delivery Date =
CALCULATE(
    [Units Ordered],
    USERELATIONSHIP(DimDate[Date], Purchase_Orders[actual_delivery_date])
)
```
*Uses actual delivery date for a delivery-period analysis instead of order date.*

## Measure interpretation

- Reorder Gap is a prioritisation indicator, not an automatic purchase recommendation.
- Delayed Order Rate uses only orders with actual delivery dates in the delayed-order measure; if open orders are introduced, define a separate open-order KPI.
- Product Inventory Value follows the project rule available quantity × unit cost, including negative available quantities for stock-out records.
