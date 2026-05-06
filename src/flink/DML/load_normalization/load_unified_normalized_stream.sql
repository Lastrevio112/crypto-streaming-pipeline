INSERT INTO unified_normalized_stream(
    trade_id, trade_time, sent_time, coin_symbol, price, quantity, data_source_id
)
SELECT 
    trade_id, trade_time, sent_time, coin_symbol, price, quantity,
    1 AS data_source_id
FROM DS1_binance_normalized_stream
UNION ALL
SELECT 
    trade_id, trade_time, sent_time, coin_symbol, price, quantity,
    2 AS data_source_id
FROM DS2_mexc_normalized_stream