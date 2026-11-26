# StockWise Power BI — Three-Page Report Design

This specification describes the report to build in Power BI Desktop from the cleaned synthetic CSV data and the model in `PowerBI_Data_Model.md`. It is a build guide, not a PBIX file.

## Report-wide design

- Canvas: 16:9 widescreen.
- Background: white or very light neutral grey.
- Primary text: dark navy; use readable font sizes and concise chart titles.
- Use labels and status text as well as colour; never rely on colour alone.
- Suggested palette: navy `#1F3A5F`, teal `#0F766E`, amber `#D97706`, red `#B91C1C`, slate `#64748B`.
- Keep a consistent header with report title, page name, and a small caption: "Synthetic teaching dataset".
- Add a reset-filters bookmark/button to each page.
- Use single-direction dimension-to-fact filtering from the data model guide.

## Page 1 — Inventory Overview

**Business questions**
- How much stock is currently available?
- How many products are out of stock or below their reorder level?
- Which categories hold the highest inventory value?
- How do incoming and outgoing stock movements vary over time?

**KPI cards**
- Total Products
- Available Units
- Stock-Out Products
- Inventory Value

**Visuals and fields**

| Visual | Type | Fields / measures | Purpose |
|---|---|---|---|
| Product stock status by category | Stacked column chart | Axis: Products[category]; Legend: Inventory[Stock Status]; Values: distinct product count | Compare healthy, low-stock and stock-out products by category. |
| Monthly stock movement | Line chart | Axis: DimDate[YearMonth]; Legend: Stock_Movements[movement_type]; Values: sum of Stock_Movements[quantity] | Compare incoming and outgoing units by month. |
| Inventory value by category | Bar chart | Axis: Products[category]; Values: [Inventory Value] | Identify categories with the highest recorded inventory value. |
| Stock snapshot detail | Table | Products[product_name], Products[category], Inventory[available_quantity], Products[reorder_level], Inventory[Stock Status] | Allow users to inspect product-level stock. |

**Slicers**
- DimDate[Date] (activity date)
- Products[category]
- Products[supplier_name] (merged in Power Query)

## Page 2 — Product & Supplier Analysis

**Business questions**
- Which products have the highest inventory value?
- Which suppliers have the longest average delivery lead time?
- Which suppliers have the most delayed purchase orders?
- Which product categories account for the largest order quantities?

**Visuals and fields**

| Visual | Type | Fields / measures | Purpose |
|---|---|---|---|
| Product value ranking | Horizontal bar chart | Axis: Products[product_name]; Values: product inventory value measure | Rank products by available quantity × unit cost. |
| Supplier lead time | Horizontal bar chart | Axis: Suppliers[supplier_name]; Values: [Average Lead Time (Days)] | Compare average delivery time by order supplier. |
| Delayed orders by supplier | Column chart | Axis: Suppliers[supplier_name]; Values: [Delayed Orders] | Identify suppliers with the most late deliveries. |
| Order value by category | Treemap or bar chart | Group: Products[category]; Values: [Ordered Value] | Compare recorded purchase-order value by category. |
| Purchase-order detail | Table | Purchase_Orders[order_id], Suppliers[supplier_name], Products[product_name], Purchase_Orders[quantity_ordered], Purchase_Orders[unit_cost], Purchase_Orders[order_date], Purchase_Orders[expected_delivery_date], Purchase_Orders[actual_delivery_date] | Support investigation of individual order lines. |

**Slicers**
- DimDate[Date] (order date by default)
- Suppliers[supplier_name] (supplier on the purchase order)
- Products[category]

**Drill-through**
- Configure a supplier drill-through target using Suppliers[supplier_id] and include supplier name, order count, average lead time, delayed orders, and purchase-order detail.
- If the report is restricted to exactly three pages, use the existing Page 2 as the supplier drill-through target or keep the supplier drill-through as a separate optional hidden page only if the evaluator permits an extra page.

## Page 3 — Stock-Out & Reorder Analysis

**Business questions**
- Which products are currently out of stock?
- Which products are below their reorder level?
- How large is the reorder gap for each at-risk product?
- Which categories have the greatest number of stock-out products?

**Visuals and fields**

| Visual | Type | Fields / measures | Purpose |
|---|---|---|---|
| Stock-out and low-stock counts | Clustered bar chart | Axis: Products[category]; Values: [Stock-Out Products], [Low-Stock Products] | Compare inventory risk across categories. |
| Highest reorder gaps | Horizontal bar chart | Axis: Products[product_name]; Values: [Reorder Gap] | Prioritise products furthest below their reorder threshold. |
| Reorder attention list | Table | Products[product_id], Products[product_name], Products[category], Products[supplier_name], Inventory[available_quantity], Products[reorder_level], Inventory[Stock Status], [Reorder Gap] | Provide an actionable product-level review list. |
| Stock status share | Donut chart | Legend: Inventory[Stock Status]; Values: distinct product count | Show the share of products in each stock status. |

**Slicers**
- Products[category]
- Products[supplier_name]
- Inventory[snapshot_date]

**Drill-through**
- Enable drill-through from product visuals using Products[product_id]. Show the product's current stock, reorder level, inventory value, supplier, and stock movement history on the target page.

## Build and formatting checklist

1. Create the three report pages and use the exact page names above.
2. Add KPI cards first, then charts, then detail tables.
3. Add slicers in a consistent position and use **View → Sync slicers** for category and date where appropriate.
4. Set chart titles to business questions, not generic labels such as "Chart 1".
5. Display units on axes; format inventory values to two decimal places and lead time to one decimal place.
6. Sort month labels chronologically using DimDate[Date] or a YearMonth sort key.
7. Turn on data labels only where they remain readable.
8. Add useful tooltips such as supplier name, order count, delayed orders, available quantity, and reorder level.
9. Configure drill-through fields and add a Back button on drill-through targets.
10. Test slicers, cross-highlighting, empty selections, and totals against Python outputs.
11. Add a small source/assumption note to each page: "Synthetic data; one inventory snapshot; no live ERP connection."
12. Save the completed report as `powerbi/StockWise.pbix`.

## Known limitations

- Inventory contains a single snapshot date, so it cannot show measured historical daily inventory levels.
- The estimated stock-out trend from the Python chart is reconstructed from opening stock and movements; it should not be presented as observed daily inventory.
- Supplier filtering for inventory and movement visuals uses supplier fields merged into Products. The Suppliers dimension filters purchase-order supplier records.
- Power BI Desktop is required to create and validate the PBIX. The repository documentation does not substitute for that binary report file.
