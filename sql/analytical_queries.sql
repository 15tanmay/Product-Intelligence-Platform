-- sql/analytical_queries.sql
-- Contains reusable SQL queries for product analytics.

-- First vs Repeat Customer Ratio
WITH customer_orders AS (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) as total_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT 
    CASE WHEN total_orders = 1 THEN 'One-Time' ELSE 'Repeat' END as customer_type,
    COUNT(customer_unique_id) as count
FROM customer_orders
GROUP BY 1;
