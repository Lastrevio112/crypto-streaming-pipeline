--The per-column computation is the same for all the windowed tables so I am adding it all to one file.

INSERT INTO derived_ohlcv_1s_tumbling(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev, sum_price, sum_price_sq
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    SUM(quantity)                                                           AS volume,
    SUM(price * quantity)                                                   AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(quantity)                                                           AS max_single_trade_quantity,
    SUM(price * quantity) / NULLIF(SUM(quantity), 0)                        AS vwap,
    SUM(CASE WHEN is_buy_or_sell = 'buy' THEN quantity END)                 AS aggressive_buy_volume,
    SUM(CASE WHEN is_buy_or_sell = 'sell' THEN quantity END)                AS aggressive_sell_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_trade_count,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_trade_count,
    STDDEV_POP_SAFE(price)                                                  AS price_std_dev,
    SUM(price)                                                              AS sum_price,
    SUM(CAST(price AS DECIMAL(18, 4)) * CAST(price AS DECIMAL(18, 4)))      AS sum_price_sq     --to avoid decimal overflow for huge values

FROM TUMBLE(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SIZE => INTERVAL '1' SECOND
)
WHERE TRY_CAST(price AS DECIMAL(21, 8)) IS NOT NULL
AND TRY_CAST(quantity AS DECIMAL(21,8)) IS NOT NULL
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_5s_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev, sum_price, sum_price_sq
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    SUM(quantity)                                                           AS volume,
    SUM(price * quantity)                                                   AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(quantity)                                                           AS max_single_trade_quantity,
    SUM(price * quantity) / NULLIF(SUM(quantity), 0)                        AS vwap,
    SUM(CASE WHEN is_buy_or_sell = 'buy' THEN quantity END)                 AS aggressive_buy_volume,
    SUM(CASE WHEN is_buy_or_sell = 'sell' THEN quantity END)                AS aggressive_sell_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_trade_count,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_trade_count,
    STDDEV_POP_SAFE(price)                                                  AS price_std_dev,
    SUM(price)                                                              AS sum_price,
    SUM(CAST(price AS DECIMAL(18, 4)) * CAST(price AS DECIMAL(18, 4)))      AS sum_price_sq     --to avoid decimal overflow for huge values

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '1' SECOND,
    SIZE => INTERVAL '5' SECOND
)
WHERE TRY_CAST(price AS DECIMAL(21, 8)) IS NOT NULL
AND TRY_CAST(quantity AS DECIMAL(21,8)) IS NOT NULL
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_1m_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev, sum_price, sum_price_sq
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    SUM(quantity)                                                           AS volume,
    SUM(price * quantity)                                                   AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(quantity)                                                           AS max_single_trade_quantity,
    SUM(price * quantity) / NULLIF(SUM(quantity), 0)                        AS vwap,
    SUM(CASE WHEN is_buy_or_sell = 'buy' THEN quantity END)                 AS aggressive_buy_volume,
    SUM(CASE WHEN is_buy_or_sell = 'sell' THEN quantity END)                AS aggressive_sell_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_trade_count,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_trade_count,
    STDDEV_POP_SAFE(price)                                                  AS price_std_dev,
    SUM(price)                                                              AS sum_price,
    SUM(CAST(price AS DECIMAL(18, 4)) * CAST(price AS DECIMAL(18, 4)))      AS sum_price_sq     --to avoid decimal overflow for huge values

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '5' SECOND,
    SIZE => INTERVAL '1' MINUTE
)
WHERE TRY_CAST(price AS DECIMAL(21, 8)) IS NOT NULL
AND TRY_CAST(quantity AS DECIMAL(21,8)) IS NOT NULL
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_5m_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev, sum_price, sum_price_sq
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    SUM(quantity)                                                           AS volume,
    SUM(price * quantity)                                                   AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(quantity)                                                           AS max_single_trade_quantity,
    SUM(price * quantity) / NULLIF(SUM(quantity), 0)                        AS vwap,
    SUM(CASE WHEN is_buy_or_sell = 'buy' THEN quantity END)                 AS aggressive_buy_volume,
    SUM(CASE WHEN is_buy_or_sell = 'sell' THEN quantity END)                AS aggressive_sell_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_trade_count,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN 1
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_trade_count,
    STDDEV_POP_SAFE(price)                                                  AS price_std_dev,
    SUM(price)                                                              AS sum_price,
    SUM(CAST(price AS DECIMAL(18, 4)) * CAST(price AS DECIMAL(18, 4)))      AS sum_price_sq     --to avoid decimal overflow for huge values

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '30' SECOND,
    SIZE => INTERVAL '5' MINUTE
)
WHERE TRY_CAST(price AS DECIMAL(21, 8)) IS NOT NULL
AND TRY_CAST(quantity AS DECIMAL(21,8)) IS NOT NULL
GROUP BY coin_symbol, window_start, window_end;