from views.AnalyticsView import AnalyticsView

class AnalyticsTumbleView(AnalyticsView):
    def __init__(self, list_of_excluded_coins: list[str], view_name: str, interval: str, src_table_name: str = 'src_1s_tumbling'):
        super().__init__(
            list_of_excluded_coins = list_of_excluded_coins, 
            view_name = view_name,
            src_table_name = src_table_name,
            interval = interval)

    def generate_sql(self) -> str:
        excluded_coins_str = ", ".join([f"'{coin}'" for coin in self.list_of_excluded_coins])

        query = f"""
            CREATE OR REPLACE VIEW {self.view_name} AS
            SELECT
            coin_symbol,
            toStartOfInterval(window_start, INTERVAL {self.interval})                               AS window_start,
            toStartOfInterval(window_start, INTERVAL {self.interval}) + INTERVAL {self.interval}    AS window_end,
            argMin(s.open_price,  window_start)             AS open_price,
            MAX(s.high_price)                               AS high_price,
            MIN(s.low_price)                                AS low_price,
            argMax(s.close_price, window_start)             AS close_price,
            SUM(volume)                                     AS volume,
            SUM(s.quote_volume)                             AS quote_volume,
            SUM(s.trade_count)                              AS trade_count,
            MAX(max_single_trade_quantity)                  AS max_single_trade_quantity,
            SUM(s.quote_volume) / NULLIF(SUM(s.volume), 0)  AS vwap,
            SUM(s.aggressive_buy_volume)                    AS aggressive_buy_volume,
            SUM(s.aggressive_sell_volume)                   AS aggressive_sell_volume,
            SUM(s.aggressive_buy_trade_count)               AS aggressive_buy_trade_count,
            SUM(s.aggressive_sell_trade_count)              AS aggressive_sell_trade_count,
            sqrt(
                GREATEST(
                    toDecimal256(SUM(s.sum_price_sq), 3) / NULLIF(SUM(s.trade_count), 0)
                    - POW(toDecimal256(SUM(s.sum_price), 3) / NULLIF(SUM(s.trade_count), 0), 2),
                    0.0
                )
            )                                               AS price_std_dev,
            SUM(s.aggressive_buy_trade_count)
            / NULLIF(SUM(s.aggressive_sell_trade_count), 0) AS buy_sell_trade_ratio,
            SUM(s.aggressive_buy_volume)
            / NULLIF(SUM(s.aggressive_sell_volume), 0)      AS buy_sell_volume_ratio,
            SUM(s.aggressive_buy_volume)
            - SUM(s.aggressive_sell_volume)                 AS net_flow,
            SUM(s.quote_volume) 
            / NULLIF(SUM(s.trade_count), 0)                 AS avg_trade_size,
            MAX(s.high_price) - MIN(s.low_price)            AS price_range,
            (argMax(s.close_price, window_start)
            - argMin(s.open_price,  window_start))
            / argMin(s.open_price,  window_start)           AS open_to_close_return
        FROM src_1s_tumbling s
        WHERE coin_symbol NOT IN ({excluded_coins_str})
        GROUP BY 1, 2, 3
        ORDER BY 1, 2;
        """
        return query
    