-- Raw sources:

CREATE TABLE IF NOT EXISTS binance_ds1_trades (
    -- https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#trade-streams
    e           STRING,        -- Event type
    `E`         BIGINT,        -- event time (time it was sent by the websocket)
    s           STRING,        -- Symbol
    t           BIGINT,        -- Trade ID
    p           STRING,        -- Price
    q           STRING,        -- Quantity
    `T`         BIGINT,        -- trade time, UNIX
    m           BOOLEAN,        -- Is the buyer the market maker?
    trade_ts AS TO_TIMESTAMP_LTZ(`T`, 3),  --not in source data, needed for watermark calculation
    WATERMARK FOR trade_ts AS trade_ts - INTERVAL '0.25' SECOND
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'binance_ds1_trades',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'flink-binance-consumer',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

CREATE TABLE IF NOT EXISTS mexc_ds2_trades (
    -- https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#trade-streams
    channel     STRING,         -- The subscribe stream URL
    symbol      STRING,
    sendtime    BIGINT,
    publicdeals ROW<
        eventtype   STRING,
        dealsList   ARRAY<ROW<
            price       STRING, -- Trade price
            quantity    STRING, -- Trade quantity
            tradetype   INT,    -- Trade type (1: Buy, 2: Sell)
            `time`      BIGINT  -- Trade time, UNIX
        >>
    >
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'mexc_ds2_trades',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'flink-mexc-consumer',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);


-- We need this view in order to get deal.trade_time at the level of the highest granularity, unnesting the deals array.
-- This is necessary in order to have consistent watermarks accross the entire pipeline (trade time, not the time the websocket sent the data).
CREATE VIEW mexc_ds2_unnested AS
SELECT
    CONCAT('mexc_', MD5(CONCAT(
        symbol,
        CAST(deal.`time` AS STRING),
        deal.price,
        deal.quantity
    )))                                                         AS trade_id,
    CAST(TO_TIMESTAMP_LTZ(deal.`time`, 3) AS TIMESTAMP(3))      AS trade_time,
    CAST(TO_TIMESTAMP_LTZ(src.sendtime, 3) AS TIMESTAMP(3))     AS sent_time,
    src.symbol                                                  AS coin_symbol,
    CAST(deal.price    AS DECIMAL(21, 8))                       AS price,
    CAST(deal.quantity AS DECIMAL(21, 8))                       AS quantity
FROM mexc_ds2_trades AS src
CROSS JOIN UNNEST(src.publicdeals.dealsList) AS deal(price, quantity, tradetype, `time`);


-- Normalized sinks (data source specific):

CREATE TABLE IF NOT EXISTS DS1_binance_normalized_stream (
    trade_id        STRING,     -- prefixed: "binance_<t>"
    trade_time      TIMESTAMP(3),
    sent_time       TIMESTAMP(3),
    proc_time    AS PROCTIME(), -- trade_time < sent_time < proc_time, always.
    coin_symbol     STRING,
    price           DECIMAL(21, 8),
    quantity        DECIMAL(21, 8),
    WATERMARK FOR trade_time AS trade_time - INTERVAL '0.25' SECOND
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'DS1_binance_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'DS1_binance_normalized_stream',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

CREATE TABLE IF NOT EXISTS DS2_mexc_normalized_stream (
    trade_id        STRING,
    trade_time      TIMESTAMP(3),
    sent_time       TIMESTAMP(3),
    proc_time    AS PROCTIME(),
    coin_symbol     STRING,
    price           DECIMAL(21, 8),
    quantity        DECIMAL(21, 8),
    WATERMARK FOR trade_time AS trade_time - INTERVAL '0.25' SECOND 
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'DS2_mexc_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'DS2_mexc_normalized_stream',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);


-- Unified sink - all trades

CREATE TABLE IF NOT EXISTS unified_normalized_stream (
    trade_id        STRING,     -- prefixed with data source name to ensure global uniqueness
    trade_time      TIMESTAMP(3),
    sent_time       TIMESTAMP(3),
    proc_time    AS PROCTIME(),
    coin_symbol     STRING,
    price           DECIMAL(21, 8),
    quantity        DECIMAL(21, 8),
    data_source_id  INT,
    WATERMARK FOR trade_time AS trade_time - INTERVAL '0.25' SECOND
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'unified_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'unified_normalized_stream',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);