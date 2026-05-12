import clickhouse_connect
from dotenv import load_dotenv
import os

from views.AnalyticsTumbleView import AnalyticsTumbleView
from views.AnalyticsSlidingView import AnalyticsSlidingView


def execute_sql_file(client: clickhouse_connect.driver.client, file_path):
    with open(file_path, 'r') as f:
        sql = f.read()
        statements = sql.split(';')
        for statement_no, statement in enumerate(statements):
            if statement.strip() and statement_no != len(statements)-1:
                client.command(statement)


def create_tumbling_views(client: clickhouse_connect.driver.client, list_of_excluded_coins: list[str]):
    intervals_and_names_for_tumbling_views = [
        ('1 SECOND', 'analytics_1s_tumbling'),
        ('5 SECOND', 'analytics_5s_tumbling'),
        ('30 SECOND', 'analytics_30s_tumbling'),
        ('1 MINUTE', 'analytics_1m_tumbling'),
        ('5 MINUTE', 'analytics_5m_tumbling'),
        ('30 MINUTE', 'analytics_30m_tumbling'),
        ('1 HOUR', 'analytics_1h_tumbling'),
        ('4 HOUR', 'analytics_4h_tumbling'),
        ('24 HOUR', 'analytics_24h_tumbling')
    ]

    for interval, view_name in intervals_and_names_for_tumbling_views:
        view = AnalyticsTumbleView(
            list_of_excluded_coins=list_of_excluded_coins,
            view_name=view_name,
            interval=interval,
            src_table_name='src_1s_tumbling'
            )
        try:
            view.execute_query(client)
        except Exception as e:
            print(e)


def create_sliding_views(client: clickhouse_connect.driver.client, list_of_excluded_coins: list[str]):
    _5s_sliding_view = AnalyticsSlidingView(
        list_of_excluded_coins=list_of_excluded_coins,
        view_name = 'analytics_5s_sliding',
        src_table_name = 'src_5s_sliding',
        interval = None
    )
    _1m_sliding_view = AnalyticsSlidingView(
        list_of_excluded_coins=list_of_excluded_coins,
        view_name = 'analytics_1m_sliding',
        src_table_name = 'src_1m_sliding',
        interval = None
    )
    _5m_sliding_view = AnalyticsSlidingView(
        list_of_excluded_coins=list_of_excluded_coins,
        view_name = 'analytics_5m_sliding',
        src_table_name = 'src_5m_sliding',
        interval = None
    )

    sliding_views = [_5s_sliding_view, _1m_sliding_view, _5m_sliding_view]
    for view in sliding_views:
        try:
            view.execute_query(client)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    load_dotenv(".env.clickhouse")

    conn = clickhouse_connect.get_client(
        interface="http",
        host=os.environ.get("CLICKHOUSE_HOST"),
        port=os.environ.get("CLICKHOUSE_PORT"),
        database=os.environ.get("CLICKHOUSE_DB"),
        username=os.environ.get("CLICKHOUSE_USER"),
        password=os.environ.get("CLICKHOUSE_PASSWORD")
    )

    list_of_paths = [
        # "DDL_src/src_1s_tumbling.sql",
        # "DDL_src/src_5s_sliding.sql",
        # "DDL_src/src_1m_sliding.sql",
        # "DDL_src/src_5m_sliding.sql"
    ]

    for path in list_of_paths:
        try:
            execute_sql_file(conn, "/workspace/src/clickhouse/" + path)
        except Exception as e:
            print(e)
    
    list_of_excluded_coins = ['币安人生USDT', 'UUSDT', 'USD1USDT']

    create_tumbling_views(conn, list_of_excluded_coins)
    create_sliding_views(conn, list_of_excluded_coins)

    conn.close()
