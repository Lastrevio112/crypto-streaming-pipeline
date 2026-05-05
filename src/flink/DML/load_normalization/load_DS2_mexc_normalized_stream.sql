-- Simple insert statement as the actual transformation/normalization logic was handled in the view DDL.
-- This is an intentional design choice in order to have consistent watermark logic accross the pipeline.
INSERT INTO DS2_mexc_normalized_stream (
    trade_id,
    trade_time,
    sent_time,
    coin_symbol,
    price,
    quantity
)
SELECT
    trade_id,
    trade_time,
    sent_time,
    coin_symbol,
    price,
    quantity
FROM mexc_ds2_unnested;