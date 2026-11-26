-- Q1: Inventory stock status by product category
SELECT
    p.category,
    COUNT(*) AS product_count,
    SUM(CASE WHEN i.available_quantity <= 0 THEN 1 ELSE 0 END) AS stockout_products,
    SUM(CASE WHEN i.available_quantity > 0
              AND i.available_quantity <= p.reorder_level THEN 1 ELSE 0 END) AS low_stock_products,
    SUM(i.available_quantity) AS total_available_quantity
FROM fact_inventory i
JOIN dim_product p ON p.product_key = i.product_key
JOIN dim_date d ON d.date_key = i.snapshot_date_key
GROUP BY p.category
ORDER BY p.category;

-- Q2: Products currently at or below their reorder level
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
JOIN dim_product p ON p.product_key = i.product_key
WHERE i.available_quantity <= p.reorder_level
ORDER BY i.available_quantity, p.category, p.product_name;

-- Q3: Inventory value by category
SELECT
    p.category,
    SUM(i.available_quantity * p.unit_cost) AS inventory_value
FROM fact_inventory i
JOIN dim_product p ON p.product_key = i.product_key
GROUP BY p.category
ORDER BY inventory_value DESC;

-- Q4: Monthly stock movement by category and movement direction
SELECT
    d.calendar_year,
    d.calendar_month,
    d.month_name,
    p.category,
    m.movement_type,
    SUM(m.quantity) AS movement_quantity,
    COUNT(*) AS movement_count
FROM fact_stock_movement m
JOIN dim_product p ON p.product_key = m.product_key
JOIN dim_date d ON d.date_key = m.movement_date_key
GROUP BY d.calendar_year, d.calendar_month, d.month_name,
         p.category, m.movement_type
ORDER BY d.calendar_year, d.calendar_month, p.category, m.movement_type;

-- Q5: Supplier delivery performance and average lead time
SELECT
    s.supplier_id,
    s.supplier_name,
    COUNT(*) AS delivered_orders,
    ROUND(AVG(d_actual.full_date - d_order.full_date), 2) AS avg_lead_time_days,
    SUM(CASE WHEN d_actual.full_date > d_expected.full_date THEN 1 ELSE 0 END) AS delayed_orders
FROM fact_purchase_order po
JOIN dim_supplier s ON s.supplier_key = po.supplier_key
JOIN dim_date d_order ON d_order.date_key = po.order_date_key
JOIN dim_date d_expected ON d_expected.date_key = po.expected_delivery_date_key
JOIN dim_date d_actual ON d_actual.date_key = po.actual_delivery_date_key
GROUP BY s.supplier_id, s.supplier_name
ORDER BY avg_lead_time_days DESC;

-- Q6: Purchase order quantity and spend by supplier and category
SELECT
    s.supplier_name,
    p.category,
    COUNT(*) AS order_lines,
    SUM(po.quantity_ordered) AS units_ordered,
    SUM(po.quantity_ordered * po.unit_cost) AS ordered_value
FROM fact_purchase_order po
JOIN dim_supplier s ON s.supplier_key = po.supplier_key
JOIN dim_product p ON p.product_key = po.product_key
GROUP BY s.supplier_name, p.category
ORDER BY ordered_value DESC;

-- Q7: Product-level stock movement totals
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(CASE WHEN m.movement_type = 'IN' THEN m.quantity ELSE 0 END) AS units_received,
    SUM(CASE WHEN m.movement_type = 'OUT' THEN m.quantity ELSE 0 END) AS units_issued,
    SUM(CASE WHEN m.movement_type = 'IN' THEN m.quantity ELSE -m.quantity END) AS net_movement
FROM fact_stock_movement m
JOIN dim_product p ON p.product_key = m.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY p.category, p.product_name;
