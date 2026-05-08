CREATE TABLE derived_ohlcv_1s_tumbling(
    coin_symbol                 STRING,
    window_start                TIMESTAMP(3),
    window_end                  TIMESTAMP(3),
    open_price                  DECIMAL(21,8),
    high_price                  DECIMAL(21,8),
    low_price                   DECIMAL(21,8),
    close_price                 DECIMAL(21,8),
    volume                      DECIMAL(21,8),
    quote_volume                DECIMAL(21,8),
    trade_count                 INT,
    max_single_trade_quantity   DECIMAL(21,8),
    vwap                        DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume       DECIMAL(21, 8),
    aggressive_sell_volume      DECIMAL(21, 8),
    aggressive_buy_trade_count  INT,
    aggressive_sell_trade_count INT,
    net_flow                    DECIMAL(21, 8),
    buy_sell_ratio              DECIMAL(21, 8),
    price_std_dev               DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.35' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_1s_tumbling',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_1s_tumbling',
    'scan.startup.mode'             = 'latest-offset',
    'value.avro-confluent.url'      = 'http://schema-registry:8081',
    'sink.partitioner'              = 'com.crypto.SymbolPartitioner',
    'key.format'                    = 'raw',
    'key.fields'                    = 'coin_symbol',
    'value.format'                  = 'avro-confluent',
    'value.fields-include'          = 'EXCEPT_KEY'
);

-- 1s sliding step
CREATE TABLE derived_ohlcv_5s_sliding(
    coin_symbol                 STRING,
    window_start                TIMESTAMP(3),
    window_end                  TIMESTAMP(3),
    open_price                  DECIMAL(21,8),
    high_price                  DECIMAL(21,8),
    low_price                   DECIMAL(21,8),
    close_price                 DECIMAL(21,8),
    volume                      DECIMAL(21,8),
    quote_volume                DECIMAL(21,8),
    trade_count                 INT,
    max_single_trade_quantity   DECIMAL(21,8),
    vwap                        DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume       DECIMAL(21, 8),
    aggressive_sell_volume      DECIMAL(21, 8),
    aggressive_buy_trade_count  INT,
    aggressive_sell_trade_count INT,
    net_flow                    DECIMAL(21, 8),
    buy_sell_ratio              DECIMAL(21, 8),
    price_std_dev               DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.35' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_5s_sliding',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_5s_sliding',
    'scan.startup.mode'             = 'latest-offset',
    'value.avro-confluent.url'      = 'http://schema-registry:8081',
    'sink.partitioner'              = 'com.crypto.SymbolPartitioner',
    'key.format'                    = 'raw',
    'key.fields'                    = 'coin_symbol',
    'value.format'                  = 'avro-confluent',
    'value.fields-include'          = 'EXCEPT_KEY'
);

-- 5s sliding step
CREATE TABLE derived_ohlcv_1m_sliding(
    coin_symbol                 STRING,
    window_start                TIMESTAMP(3),
    window_end                  TIMESTAMP(3),
    open_price                  DECIMAL(21,8),
    high_price                  DECIMAL(21,8),
    low_price                   DECIMAL(21,8),
    close_price                 DECIMAL(21,8),
    volume                      DECIMAL(21,8),
    quote_volume                DECIMAL(21,8),
    trade_count                 INT,
    max_single_trade_quantity   DECIMAL(21,8),
    vwap                        DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume       DECIMAL(21, 8),
    aggressive_sell_volume      DECIMAL(21, 8),
    aggressive_buy_trade_count  INT,
    aggressive_sell_trade_count INT,
    net_flow                    DECIMAL(21, 8),
    buy_sell_ratio              DECIMAL(21, 8),
    price_std_dev               DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '0.75' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_1m_sliding',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_1m_sliding',
    'scan.startup.mode'             = 'latest-offset',
    'value.avro-confluent.url'      = 'http://schema-registry:8081',
    'sink.partitioner'              = 'com.crypto.SymbolPartitioner',
    'key.format'                    = 'raw',
    'key.fields'                    = 'coin_symbol',
    'value.format'                  = 'avro-confluent',
    'value.fields-include'          = 'EXCEPT_KEY'
);

-- 30s sliding step
CREATE TABLE derived_ohlcv_5m_sliding(
    coin_symbol                 STRING,
    window_start                TIMESTAMP(3),
    window_end                  TIMESTAMP(3),
    open_price                  DECIMAL(21,8),
    high_price                  DECIMAL(21,8),
    low_price                   DECIMAL(21,8),
    close_price                 DECIMAL(21,8),
    volume                      DECIMAL(21,8),
    quote_volume                DECIMAL(21,8),
    trade_count                 INT,
    max_single_trade_quantity   DECIMAL(21,8),
    vwap                        DECIMAL(21,8),      --"volume weighted average price"         
    aggressive_buy_volume       DECIMAL(21, 8),
    aggressive_sell_volume      DECIMAL(21, 8),
    aggressive_buy_trade_count  INT,
    aggressive_sell_trade_count INT,
    net_flow                    DECIMAL(21, 8),
    buy_sell_ratio              DECIMAL(21, 8),
    price_std_dev               DECIMAL(21, 8),
    PRIMARY KEY (coin_symbol, window_start) NOT ENFORCED,
    WATERMARK FOR window_end AS window_end - INTERVAL '1' SECOND
)
WITH (
    'connector'                     = 'upsert-kafka',
    'topic'                         = 'derived_ohlcv_5m_sliding',
    'properties.bootstrap.servers'  = 'kafka:9092',
    'properties.group.id'           = 'derived_ohlcv_5m_sliding',
    'scan.startup.mode'             = 'latest-offset',
    'value.avro-confluent.url'      = 'http://schema-registry:8081',
    'sink.partitioner'              = 'com.crypto.SymbolPartitioner',
    'key.format'                    = 'raw',
    'key.fields'                    = 'coin_symbol',
    'value.format'                  = 'avro-confluent',
    'value.fields-include'          = 'EXCEPT_KEY'
);