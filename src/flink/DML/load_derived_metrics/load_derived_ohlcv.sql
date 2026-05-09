--The per-column computation is the same for all the windowed tables so I am adding it all to one file.

INSERT INTO derived_ohlcv_1s_tumbling(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    COALESCE(SUM(quantity), 0.0)                                            AS volume,
    SUM(price * COALESCE(quantity, 0.0))                                    AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(COALESCE(quantity, 0.0))                                            AS max_single_trade_quantity,
    COALESCE(
        SUM(price * quantity) / COALESCE(SUM(quantity), 1),
        0.0
        )                                                                   AS vwap,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_volume,
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
    CASE
        WHEN STDDEV_POP(price) <> STDDEV_POP(price) THEN -1.0  --Nan=NaN is false
        ELSE COALESCE(STDDEV_POP(price), -1.0)
    END                                                                     AS price_std_dev

FROM TUMBLE(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SIZE => INTERVAL '1' SECOND
)
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_5s_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    COALESCE(SUM(quantity), 0.0)                                            AS volume,
    SUM(price * COALESCE(quantity, 0.0))                                    AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(COALESCE(quantity, 0.0))                                            AS max_single_trade_quantity,
    COALESCE(
        SUM(price * quantity) / COALESCE(SUM(quantity), 1),
        0.0
        )                                                                   AS vwap,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_volume,
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
    CASE
        WHEN STDDEV_POP(price) <> STDDEV_POP(price) THEN -1.0  --Nan=NaN is false
        ELSE COALESCE(STDDEV_POP(price), -1.0)
    END                                                                     AS price_std_dev

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '1' SECOND,
    SIZE => INTERVAL '5' SECOND
)
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_1m_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    COALESCE(SUM(quantity), 0.0)                                            AS volume,
    SUM(price * COALESCE(quantity, 0.0))                                    AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(COALESCE(quantity, 0.0))                                            AS max_single_trade_quantity,
    COALESCE(
        SUM(price * quantity) / COALESCE(SUM(quantity), 1),
        0.0
        )                                                                   AS vwap,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_volume,
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
    CASE
        WHEN STDDEV_POP(price) <> STDDEV_POP(price) THEN -1.0  --Nan=NaN is false
        ELSE COALESCE(STDDEV_POP(price), -1.0)
    END                                                                     AS price_std_dev

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '5' SECOND,
    SIZE => INTERVAL '1' MINUTE
)
GROUP BY coin_symbol, window_start, window_end;


INSERT INTO derived_ohlcv_5m_sliding(
    coin_symbol, window_start, window_end, open_price, high_price, low_price, close_price, volume, 
    quote_volume, trade_count, max_single_trade_quantity, vwap, aggressive_buy_volume, aggressive_sell_volume, 
    aggressive_buy_trade_count, aggressive_sell_trade_count, price_std_dev
)
SELECT
    coin_symbol,
    window_start,
    window_end,
    FIRST_VALUE_TS(price, trade_time)                                       AS open_price,     
    MAX(price)                                                              AS high_price,
    MIN(price)                                                              AS low_price,
    LAST_VALUE_TS(price, trade_time)                                        AS close_price,     
    COALESCE(SUM(quantity), 0.0)                                            AS volume,
    SUM(price * COALESCE(quantity, 0.0))                                    AS quote_volume,
    CAST(COUNT(*) AS INT)                                                   AS trade_count,
    MAX(COALESCE(quantity, 0.0))                                            AS max_single_trade_quantity,
    COALESCE(
        SUM(price * quantity) / COALESCE(SUM(quantity), 1),
        0.0
        )                                                                   AS vwap,
    SUM(
        CASE WHEN is_buy_or_sell = 'buy' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_buy_volume,
    SUM(
        CASE WHEN is_buy_or_sell = 'sell' THEN quantity
        ELSE 0 
        END
    )                                                                       AS aggressive_sell_volume,
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
    CASE
        WHEN STDDEV_POP(price) <> STDDEV_POP(price) THEN -1.0  --Nan=NaN is false
        ELSE COALESCE(STDDEV_POP(price), -1.0)
    END                                                                     AS price_std_dev

FROM HOP(
    DATA => TABLE unified_normalized_stream,
    TIMECOL => DESCRIPTOR(trade_time),
    SLIDE => INTERVAL '30' SECOND,
    SIZE => INTERVAL '5' MINUTE
)
GROUP BY coin_symbol, window_start, window_end;