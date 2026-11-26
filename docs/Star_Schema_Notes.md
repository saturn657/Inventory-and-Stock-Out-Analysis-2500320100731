# StockWise Star Schema

## Design

The model contains three dimensions and three fact tables.

| Table | Type | Grain | Primary key |
|---|---|---|---|
| DIM_PRODUCT | Dimension | One row per product | product_key |
| DIM_SUPPLIER | Dimension | One row per supplier | supplier_key |
| DIM_DATE | Dimension | One row per calendar date | date_key |
| FACT_INVENTORY | Fact | One product inventory snapshot | inventory_id |
| FACT_STOCK_MOVEMENT | Fact | One stock movement event | movement_id |
| FACT_PURCHASE_ORDER | Fact | One purchase order line | order_id |

## Relationships

- DIM_PRODUCT 1-to-many FACT_INVENTORY.
- DIM_DATE 1-to-many FACT_INVENTORY through snapshot_date_key.
- DIM_PRODUCT 1-to-many FACT_STOCK_MOVEMENT.
- DIM_DATE 1-to-many FACT_STOCK_MOVEMENT through movement_date_key.
- DIM_PRODUCT 1-to-many FACT_PURCHASE_ORDER.
- DIM_SUPPLIER 1-to-many FACT_PURCHASE_ORDER.
- DIM_DATE has three role-playing relationships to FACT_PURCHASE_ORDER: order date, expected delivery date, and actual delivery date.

## Key choices

- Surrogate numeric keys are used for dimensions; source identifiers remain as unique natural keys.
- Date keys use YYYYMMDD numeric format.
- Available quantity may be negative because it is used to identify stock-outs. Other inventory quantity components must be non-negative.
- Movement quantity must be positive; movement_type determines whether stock enters or leaves inventory.
- Purchase order actual delivery date is nullable to support open orders, even though the initial synthetic dataset contains dates for its generated orders.
- The SQL is written for Oracle Database 12c or later. Identity columns are used for dimension surrogate keys.

## Create the schema

Run `sql/schema.sql` in the dedicated Oracle project schema. Load dimensions before facts. Populate DIM_DATE for every date referenced by inventory snapshots, stock movements, and all purchase-order date roles.
