INSERT INTO DS1_binance_normalized_stream(
    trade_id, trade_time, sent_time, coin_symbol, price, quantity
)
SELECT
    CONCAT('binance_', CAST(t AS STRING))                   AS trade_id,
    CAST(TO_TIMESTAMP_LTZ(`T`, 3) AS TIMESTAMP(3))          AS trade_time,  --we have to double-cast here as avro-confluent has trouble parsing timestamp_ltz
    CAST(TO_TIMESTAMP_LTZ(`E`, 3) AS TIMESTAMP(3))          AS sent_time,   --time it was sent by the websocket
    s                                                       AS coin_symbol,
    CAST(p AS DECIMAL(18, 8))                               AS price,
    CAST(q AS DECIMAL(18, 8))                               AS quantity
FROM binance_ds1_trades