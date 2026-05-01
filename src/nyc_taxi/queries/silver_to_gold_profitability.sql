-- :name get_zone_revenue_metrics
WITH combined AS (
    SELECT 
        'Yellow' AS service_type,
        pickup_location_id,
        pickup_zone AS zone,
        pickup_borough AS borough,
        total_amount,
        fare_amount,
        tip_amount
    FROM silver.yellow_trips
    UNION ALL
    SELECT 
    'Green' AS service_type,
        pickup_location_id,
        pickup_zone AS zone,
        pickup_borough AS borough,
        total_amount,
        fare_amount,
        tip_amount
    FROM silver.green_trips
)
SELECT
    service_type,
    pickup_location_id,
    zone,
    borough,
    COUNT(*) AS trip_count,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(tip_amount), 2) AS avg_tip
FROM combined
GROUP BY ALL
ORDER BY total_revenue DESC;