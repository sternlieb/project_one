SELECT
    username,
    COUNT(*) as event_count
FROM events
GROUP BY 1
