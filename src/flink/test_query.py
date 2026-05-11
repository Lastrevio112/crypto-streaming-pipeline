from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.common import Configuration

FLINK_REST = "http://jobmanager:8081"
SAVEPOINT_DIR = "file:///tmp/flink-savepoints"
JOB_NAME = "test_pipeline"

# Setup
config = Configuration()
config.set_string("rest.address", "jobmanager")
config.set_string("rest.port", "8081")
config.set_string("pipeline.name", JOB_NAME)
config.set_string("execution.runtime-mode", "streaming")
config.set_string("execution.target", "remote")

env = StreamExecutionEnvironment.get_execution_environment(config)

t_env = StreamTableEnvironment.create(env)

t_env.execute_sql("""
    CREATE TABLE unified_normalized_stream (
        trade_time TIMESTAMP(3),
        sent_time  TIMESTAMP(3),
        event_time TIMESTAMP(3)
    )
    WITH (
        'connector' = 'kafka',
        'topic' = 'unified_normalized_stream',
        'properties.bootstrap.servers' = 'kafka:9092',
        'properties.group.id' = 'flink-test-adhoc',
        'scan.startup.mode' = 'earliest-offset',
        'format' = 'avro-confluent',
        'avro-confluent.url' = 'http://schema-registry:8081'
    )
""")

t_env.execute_sql("""
    CREATE TABLE print_sink (
        `hour`              BIGINT,
        avg_lag_seconds     DOUBLE,
        max_lag_seconds     DOUBLE,
        avg_websocket_lag   DOUBLE
    ) WITH ('connector' = 'print')
""")

t_env.execute_sql("""
    INSERT INTO print_sink
    SELECT 
        EXTRACT(HOUR FROM trade_time),
        AVG(TIMESTAMPDIFF(SECOND, CAST(trade_time AS TIMESTAMP_LTZ(3)), PROCTIME())),
        MAX(TIMESTAMPDIFF(SECOND, CAST(trade_time AS TIMESTAMP_LTZ(3)), PROCTIME())),
        AVG(TIMESTAMPDIFF(SECOND, trade_time, sent_time))
    FROM unified_normalized_stream
    GROUP BY EXTRACT(HOUR FROM trade_time)
""")