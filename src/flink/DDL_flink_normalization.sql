-- Raw sources:

CREATE TABLE IF NOT EXISTS binance_ds1_trades (
    -- https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#trade-streams
    e       STRING,        -- Event type
    `E`     BIGINT,        -- event time (time it was sent by the websocket)
    s       STRING,        -- Symbol
    t       BIGINT,        -- Trade ID
    p       STRING,        -- Price
    q       STRING,        -- Quantity
    `T`     BIGINT,        -- trade time, UNIX
    m       BOOLEAN        -- Is the buyer the market maker?
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
            trade_time        BIGINT  -- Trade time, UNIX
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


-- Normalized sinks (data source specific):

CREATE TABLE IF NOT EXISTS DS1_binance_normalized_stream (
    sent_time       BIGINT,
    coin_symbol     STRING,
    trade_id        STRING,     -- prefixed: "binance_<t>"
    price           DECIMAL(18, 8),
    quantity        DECIMAL(18, 8),
    trade_time      BIGINT,
    `data_source`     STRING
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'DS1_binance_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

CREATE TABLE IF NOT EXISTS DS2_mexc_normalized_stream (
    sent_time       BIGINT,
    coin_symbol     STRING,
    trade_id        STRING,     -- prefixed: "mexc_<sha256_hash>"
    price           DECIMAL(18, 8),
    quantity        DECIMAL(18, 8),
    trade_time      BIGINT,
    `data_source`     STRING
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'DS2_mexc_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

-- Unified sink - all trades

CREATE TABLE IF NOT EXISTS unified_normalized_stream (
    sent_time       BIGINT,
    coin_symbol     STRING,
    trade_id        STRING,
    price           DECIMAL(18, 8),
    quantity        DECIMAL(18, 8),
    trade_time      BIGINT,
    `data_source`     STRING
) WITH (
    'connector'                     = 'kafka',
    'topic'                         = 'unified_normalized_stream',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);