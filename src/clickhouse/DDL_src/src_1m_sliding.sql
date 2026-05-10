CREATE TABLE IF NOT EXISTS kafka_derived_ohlcv_1m_sliding
(
    coin_symbol                 LowCardinality(String),
    window_start                DateTime64(3),
    window_end                  DateTime64(3),
    open_price                  Decimal(21, 8),
    high_price                  Decimal(21, 8),
    low_price                   Decimal(21, 8),
    close_price                 Decimal(21, 8),
    volume                      Decimal(21, 8),
    quote_volume                Decimal(21, 8),
    trade_count                 Int32,
    max_single_trade_quantity   Decimal(21, 8),
    vwap                        Decimal(21, 8),
    aggressive_buy_volume       Decimal(21, 8),
    aggressive_sell_volume      Decimal(21, 8),
    aggressive_buy_trade_count  Int32,
    aggressive_sell_trade_count Int32,
    price_std_dev               Float64
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list               = 'kafka:9092',
    kafka_topic_list                = 'derived_ohlcv_1m_sliding',
    kafka_group_name                = 'clickhouse_ohlcv_1m_sliding',
    kafka_format                    = 'AvroConfluent',
    format_avro_schema_registry_url = 'http://schema-registry:8081',
    kafka_num_consumers             = 1,
    kafka_skip_broken_messages      = 1;   -- skip tombstones / malformed msgs

CREATE TABLE IF NOT EXISTS src_1m_sliding
(
    coin_symbol                 LowCardinality(String),
    window_start                DateTime64(3),
    window_end                  DateTime64(3),
    open_price                  Decimal(21, 8),
    high_price                  Decimal(21, 8),
    low_price                   Decimal(21, 8),
    close_price                 Decimal(21, 8),
    volume                      Decimal(21, 8),
    quote_volume                Decimal(21, 8),
    trade_count                 Int32,
    max_single_trade_quantity   Decimal(21, 8),
    vwap                        Decimal(21, 8),
    aggressive_buy_volume       Decimal(21, 8),
    aggressive_sell_volume      Decimal(21, 8),
    aggressive_buy_trade_count  Int32,
    aggressive_sell_trade_count Int32,
    price_std_dev               Float64,
    _ingested_at                DateTime DEFAULT now()
)
ENGINE = MergeTree      -- Faster than ReplaceMergeTree, and we don't care about exactly-once semantics as we can effortlessly filter duplicates downstream
PARTITION BY toDate(window_start)
ORDER BY (coin_symbol, window_start)
TTL toDateTime(window_end) + INTERVAL 14 DAY    -- Data is deleted after 14 days
SETTINGS index_granularity = 8192;


CREATE MATERIALIZED VIEW mv_src_1m_sliding
TO src_1m_sliding
AS
SELECT
    coin_symbol,
    window_start,
    window_end,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    quote_volume,
    trade_count,
    max_single_trade_quantity,
    vwap,
    aggressive_buy_volume,
    aggressive_sell_volume,
    aggressive_buy_trade_count,
    aggressive_sell_trade_count,
    price_std_dev
FROM kafka_derived_ohlcv_1m_sliding
WHERE coin_symbol != '';   -- filter tombstone/empty messages
