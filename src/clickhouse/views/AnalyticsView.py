""" Since the view definition is the same for all tumbling windows/time intervals, 
let's avoid code duplication by writing dynamic SQL using Python."""

import clickhouse_connect
from abc import ABC, abstractmethod

class AnalyticsView(ABC):
    # Interval should be passed exactly as you would write it in Clickhouse after the word INTERVAL, 
    # for example: '4 HOUR'
    def __init__(self, list_of_excluded_coins: list[str], view_name: str, src_table_name: str, interval: str):
        self.interval = interval
        self.list_of_excluded_coins = list_of_excluded_coins
        self.src_table_name = src_table_name
        self.view_name = view_name
        self.query = self.generate_sql()

    @abstractmethod
    def generate_sql(self) -> str:
        # We have different queries for tumbling and sliding views
        pass
    
    def execute_query(self, client: clickhouse_connect.driver.client):
        client.command(self.query)
    
