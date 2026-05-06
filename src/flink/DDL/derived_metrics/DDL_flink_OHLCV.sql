CREATE TABLE derived_ohlcv_1m_tumbling(
    coin_symbol             STRING,
    window_start            TIMESTAMP(3),
    window_end              TIMESTAMP(3),
    open_price              DECIMAL(21,8),
    high_price              DECIMAL(21,8),
    low_price               DECIMAL(21,8),
    close_price             DECIMAL(21,8),
    volume                  BIGINT,
    quote_volume            DECIMAL(21,8),
    trade_count             INT,
    vwap                    DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume   DECIMAL(21, 8),
    aggressive_sell_volume  DECIMAL(21, 8),
    net_flow                DECIMAL(21, 8),
    buy_sell_ratio          DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.35' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_1m_tumbling',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_1m_tumbling',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

CREATE TABLE derived_ohlcv_5m_tumbling(
    coin_symbol             STRING,
    window_start            TIMESTAMP(3),
    window_end              TIMESTAMP(3),
    open_price              DECIMAL(21,8),
    high_price              DECIMAL(21,8),
    low_price               DECIMAL(21,8),
    close_price             DECIMAL(21,8),
    volume                  BIGINT,
    quote_volume            DECIMAL(21,8),
    trade_count             INT,
    vwap                    DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume   DECIMAL(21, 8),
    aggressive_sell_volume  DECIMAL(21, 8),
    net_flow                DECIMAL(21, 8),
    buy_sell_ratio          DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.35' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_1m_tumbling',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_1m_tumbling',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);

CREATE TABLE derived_ohlcv_5m_sliding(
    coin_symbol             STRING,
    window_start            TIMESTAMP(3),
    window_end              TIMESTAMP(3),
    open_price              DECIMAL(21,8),
    high_price              DECIMAL(21,8),
    low_price               DECIMAL(21,8),
    close_price             DECIMAL(21,8),
    volume                  BIGINT,
    quote_volume            DECIMAL(21,8),
    trade_count             INT,
    vwap                    DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume   DECIMAL(21, 8),
    aggressive_sell_volume  DECIMAL(21, 8),
    net_flow                DECIMAL(21, 8),
    buy_sell_ratio          DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.35' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_1m_tumbling',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_1m_tumbling',
    'scan.startup.mode'             = 'latest-offset',
    'format'                        = 'avro-confluent',
    'avro-confluent.url'            = 'http://schema-registry:8081'
);