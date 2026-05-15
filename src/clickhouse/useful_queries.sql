/* Nothing runs in production here - there are useful debugging or development queries that can be copy-pasted into Clickhouse's UI */

--Size of each table on disk:
SELECT
    table,
    formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC;

--Number of records per hour per table (change table name as you wish):
SELECT 
    dateName('day', _ingested_at) AS ingestedDate,
    dateName('hour', _ingested_at) AS ingestedHour,
    COUNT(*)
FROM src_5s_sliding
GROUP BY dateName('day', _ingested_at), dateName('hour', _ingested_at)
ORDER BY 1 ASC, 2 ASC;

--How much data on disk is added in the last 2 hours:
SELECT
    toStartOfHour(event_time) AS hour,
    formatReadableSize(sum(size_in_bytes)) AS disk_size_added,
    sum(rows) AS rows_added
FROM system.part_log
WHERE table IN ('src_5s_sliding', 'src_1m_sliding', 'src_5m_sliding', 'src_1s_tumbling')
  AND event_type = 'NewPart' -- Only count initial writes, not merges
  AND event_time > now() - INTERVAL 2 HOUR
GROUP BY hour
ORDER BY hour DESC;

--How much data is late:
SELECT
    avg(dateDiff('millisecond', window_end, _ingested_at)) / 1000.0 AS avg_diff_seconds,
    quantiles(0.25, 0.5, 0.75, 0.9)(dateDiff('millisecond', window_end, _ingested_at) / 1000.0) AS quantiles
FROM src_5s_sliding
WHERE _ingested_at >= now64(3) - INTERVAL 1 HOUR;