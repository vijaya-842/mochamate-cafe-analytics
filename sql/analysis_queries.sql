-- MochaMate Cafe Analytics — SQL Query Library
-- Database: SQLite / PostgreSQL compatible
-- Author: Vijaya Lakshmi Atluri

-- ─────────────────────────────────────────────────────────────
-- 1. REVENUE SUMMARY
-- ─────────────────────────────────────────────────────────────

-- Total revenue, orders, and average order value
SELECT
    COUNT(DISTINCT order_id)                        AS total_orders,
    ROUND(SUM(total_revenue), 2)                    AS total_revenue,
    ROUND(AVG(total_revenue), 2)                    AS avg_order_value,
    ROUND(SUM(total_revenue) / COUNT(DISTINCT date), 2) AS avg_daily_revenue
FROM cafe_sales;

-- Monthly revenue with month-over-month growth
WITH monthly AS (
    SELECT
        month, month_name,
        SUM(total_revenue) AS revenue,
        COUNT(DISTINCT order_id) AS orders
    FROM cafe_sales
    GROUP BY month, month_name
)
SELECT
    month_name,
    ROUND(revenue, 2)                                          AS revenue,
    orders,
    ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2)    AS mom_change,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        / LAG(revenue) OVER (ORDER BY month) * 100, 2
    )                                                          AS mom_growth_pct
FROM monthly
ORDER BY month;

-- ─────────────────────────────────────────────────────────────
-- 2. MENU PERFORMANCE
-- ─────────────────────────────────────────────────────────────

-- Top 10 items by revenue with category and revenue share
WITH item_stats AS (
    SELECT
        item_name,
        category,
        SUM(total_revenue)        AS total_revenue,
        COUNT(order_id)           AS total_orders,
        AVG(unit_price)           AS avg_price,
        AVG(quantity)             AS avg_qty
    FROM cafe_sales
    GROUP BY item_name, category
),
totals AS (SELECT SUM(total_revenue) AS grand_total FROM item_stats)
SELECT
    i.item_name,
    i.category,
    ROUND(i.total_revenue, 2)                          AS revenue,
    i.total_orders,
    ROUND(i.avg_price, 2)                              AS avg_price,
    ROUND(i.total_revenue / t.grand_total * 100, 2)   AS revenue_share_pct,
    RANK() OVER (ORDER BY i.total_revenue DESC)        AS revenue_rank
FROM item_stats i, totals t
ORDER BY i.total_revenue DESC
LIMIT 10;

-- Underperforming items (< 2% revenue share)
WITH item_rev AS (
    SELECT item_name, SUM(total_revenue) AS rev FROM cafe_sales GROUP BY item_name
),
total AS (SELECT SUM(rev) AS grand_total FROM item_rev)
SELECT
    i.item_name,
    ROUND(i.rev, 2)                         AS revenue,
    ROUND(i.rev / t.grand_total * 100, 2)   AS revenue_pct
FROM item_rev i, total t
WHERE i.rev / t.grand_total * 100 < 2.0
ORDER BY i.rev;

-- ─────────────────────────────────────────────────────────────
-- 3. PEAK HOUR & DAY ANALYSIS
-- ─────────────────────────────────────────────────────────────

-- Orders and revenue by hour
SELECT
    hour,
    COUNT(order_id)           AS total_orders,
    ROUND(SUM(total_revenue), 2) AS revenue,
    ROUND(AVG(total_revenue), 2) AS avg_order_value
FROM cafe_sales
GROUP BY hour
ORDER BY hour;

-- Busiest hours (top 5)
SELECT hour, COUNT(order_id) AS orders
FROM cafe_sales
GROUP BY hour
ORDER BY orders DESC
LIMIT 5;

-- Revenue by day of week
SELECT
    day_of_week,
    COUNT(DISTINCT date)              AS num_days,
    COUNT(order_id)                   AS total_orders,
    ROUND(SUM(total_revenue), 2)      AS revenue,
    ROUND(AVG(total_revenue), 2)      AS avg_order_value,
    ROUND(SUM(total_revenue) / COUNT(DISTINCT date), 2) AS avg_daily_revenue
FROM cafe_sales
GROUP BY day_of_week
ORDER BY CASE day_of_week
    WHEN "Monday"    THEN 1 WHEN "Tuesday"   THEN 2
    WHEN "Wednesday" THEN 3 WHEN "Thursday"  THEN 4
    WHEN "Friday"    THEN 5 WHEN "Saturday"  THEN 6
    WHEN "Sunday"    THEN 7 END;

-- ─────────────────────────────────────────────────────────────
-- 4. CUSTOMER & LOYALTY ANALYSIS
-- ─────────────────────────────────────────────────────────────

-- Loyalty vs non-loyalty spend comparison
SELECT
    CASE WHEN loyalty_card = 1 THEN "Loyalty Member" ELSE "Non-Member" END AS segment,
    COUNT(order_id)                  AS total_orders,
    ROUND(SUM(total_revenue), 2)     AS total_revenue,
    ROUND(AVG(total_revenue), 2)     AS avg_order_value
FROM cafe_sales
GROUP BY loyalty_card;

-- Payment method breakdown
SELECT
    payment_method,
    COUNT(order_id)                                            AS orders,
    ROUND(SUM(total_revenue), 2)                              AS revenue,
    ROUND(COUNT(order_id) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS order_share_pct
FROM cafe_sales
GROUP BY payment_method
ORDER BY orders DESC;
