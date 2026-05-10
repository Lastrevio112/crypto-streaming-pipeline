import clickhouse_connect
from dotenv import load_dotenv
import os

def execute_sql_file(client: clickhouse_connect.driver.client, file_path):
    with open(file_path, 'r') as f:
        sql = f.read()
        for statement in sql.split(';'):
            if statement.strip():
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
        #I will fill this in later
    ]

    for path in list_of_paths:
        execute_sql_file(conn, "/workspace/src/clickhouse/" + path)

    conn.close()
