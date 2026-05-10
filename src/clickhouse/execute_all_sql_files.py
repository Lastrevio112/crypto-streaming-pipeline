import clickhouse_connect
from dotenv import load_dotenv
import os

load_dotenv(".env.clickhouse")

conn = clickhouse_connect.get_client(
    interface="http",
    host=os.environ.get("CLICKHOUSE_HOST"),
    port=os.environ.get("CLICKHOUSE_PORT"),
    database=os.environ.get("CLICKHOUSE_DB"),
    username=os.environ.get("CLICKHOUSE_USER"),
    password=os.environ.get("CLICKHOUSE_PASSWORD")
)