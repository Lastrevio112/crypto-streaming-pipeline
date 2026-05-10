import clickhouse_connect
from dotenv import load_dotenv
import os

def execute_sql_file(client: clickhouse_connect.driver.client, file_path):
    with open(file_path, 'r') as f:
        sql = f.read()
        statements = sql.split(';')
        for statement_no, statement in enumerate(statements):
            if statement.strip() and statement_no != len(statements)-1:
                client.command(statement)

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
        "DDL_src/src_1s_tumbling.sql",
        "DDL_src/src_5s_sliding.sql",
        "DDL_src/src_1m_sliding.sql",
        "DDL_src/src_5m_sliding.sql"
    ]

    for path in list_of_paths:
        try:
            execute_sql_file(conn, "/workspace/src/clickhouse/" + path)
        except Exception as e:
            print(e)

    conn.close()
