-- StockWise PL/SQL reporting procedure
-- Execute in the same Oracle schema after sql/schema.sql has been run.

CREATE OR REPLACE PROCEDURE sp_get_low_stock_products (
    p_result OUT SYS_REFCURSOR
)
AS
BEGIN
    OPEN p_result FOR
        SELECT
            p.product_id,
            p.sku,
            p.product_name,
            p.category,
            i.available_quantity,
            p.reorder_level,
            CASE
                WHEN i.available_quantity <= 0 THEN 'STOCK-OUT'
                ELSE 'LOW STOCK'
            END AS stock_status
        FROM fact_inventory i
        JOIN dim_product p
          ON p.product_key = i.product_key
        WHERE i.available_quantity <= p.reorder_level
        ORDER BY i.available_quantity, p.category, p.product_name;
END;
/
