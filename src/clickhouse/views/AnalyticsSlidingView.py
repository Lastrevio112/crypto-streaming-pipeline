from views.AnalyticsView import AnalyticsView

class AnalyticsSlidingView(AnalyticsView):
    def __init__(self, list_of_excluded_coins: list[str], view_name: str, src_table_name: str, interval: str = None):
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
            window_start,
            window_end,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            quote_volume,
            trade_count,
            max_single_trade_quantity,
            vwap,
            aggressive_buy_volume,
            aggressive_sell_volume,
            aggressive_buy_trade_count,
            aggressive_sell_trade_count,
            price_std_dev,
            aggressive_buy_trade_count / NULLIF(aggressive_sell_trade_count, 0)    AS buy_sell_trade_ratio,
            aggressive_buy_volume / NULLIF(aggressive_sell_volume, 0)              AS buy_sell_volume_ratio,
            aggressive_buy_volume - aggressive_sell_volume                         AS net_flow,
            quote_volume / NULLIF(trade_count, 0)                                  AS avg_trade_size,
            high_price - low_price                                                 AS price_range,
            (close_price - open_price) / open_price                                AS open_to_close_return,
            _ingested_at
        FROM {self.src_table_name} s
        WHERE coin_symbol NOT IN ({excluded_coins_str})
        """
        return query
    