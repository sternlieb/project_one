-- Events Per Day Analytics Query
-- This query provides the count of events (questions asked) per day
-- Includes both recent data and historical aggregation

-- Basic events per day query
SELECT
    DATE(timestamp) as event_date,
    COUNT(*) as event_count,
    COUNT(DISTINCT username) as unique_users,
    MIN(timestamp) as first_event_time,
    MAX(timestamp) as last_event_time
FROM events
GROUP BY DATE(timestamp)
ORDER BY event_date DESC;

-- Events per day for the last 30 days
SELECT
    DATE(timestamp) as event_date,
    COUNT(*) as event_count,
    COUNT(DISTINCT username) as unique_users,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT username), 2) as avg_events_per_user
FROM events
WHERE timestamp >= datetime('now', '-30 days')
GROUP BY DATE(timestamp)
ORDER BY event_date DESC;

-- Events per day with running totals
SELECT
    DATE(timestamp) as event_date,
    COUNT(*) as daily_events,
    SUM(COUNT(*)) OVER (ORDER BY DATE(timestamp)) as running_total,
    COUNT(DISTINCT username) as unique_users_today
FROM events
GROUP BY DATE(timestamp)
ORDER BY event_date DESC;

-- Top 10 days by event volume
SELECT
    DATE(timestamp) as event_date,
    COUNT(*) as event_count,
    COUNT(DISTINCT username) as unique_users,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT username), 2) as avg_events_per_user,
    GROUP_CONCAT(DISTINCT username) as users_list
FROM events
GROUP BY DATE(timestamp)
ORDER BY event_count DESC
LIMIT 10;

-- Weekly aggregation (events per week)
SELECT
    strftime('%Y-W%W', timestamp) as week,
    DATE(timestamp, 'weekday 0', '-6 days') as week_start,
    DATE(timestamp, 'weekday 0') as week_end,
    COUNT(*) as weekly_events,
    COUNT(DISTINCT username) as unique_users_week,
    COUNT(DISTINCT DATE(timestamp)) as active_days
FROM events
GROUP BY strftime('%Y-W%W', timestamp)
ORDER BY week DESC;

-- Monthly aggregation (events per month)
SELECT
    strftime('%Y-%m', timestamp) as month,
    COUNT(*) as monthly_events,
    COUNT(DISTINCT username) as unique_users_month,
    COUNT(DISTINCT DATE(timestamp)) as active_days,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT DATE(timestamp)), 2) as avg_events_per_day
FROM events
GROUP BY strftime('%Y-%m', timestamp)
ORDER BY month DESC;
