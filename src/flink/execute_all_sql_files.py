from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.common import Configuration
from pyflink.datastream import CheckpointConfig, CheckpointingMode, ExternalizedCheckpointRetention
import os
import requests
import time

FLINK_REST = "http://jobmanager:8081"
SAVEPOINT_DIR = "file:///tmp/flink-savepoints"
JOB_NAME = "flink_pipeline"

# Setup
config = Configuration()
config.set_string("rest.address", "jobmanager")
config.set_string("rest.port", "8081")
config.set_string("pipeline.name", JOB_NAME)
config.set_string("execution.runtime-mode", "streaming")
config.set_string("execution.target", "remote")

# Here we keep all checkpoints in the same filesystem and sub-folder that will be mounted to a Docker volume. 
# This is so all jobs can re-use the same checkpoint config, even if a container is rebuilt. 
# Since we only have one DAG/pipeline, centralizing all our checkpoints into one place is not an issue.
config.set_string("execution.checkpointing.storage", "filesystem")
config.set_string("execution.checkpointing.dir", "file:///opt/flink/checkpoints")

env = StreamExecutionEnvironment.get_execution_environment(config)

# Checkpointing setup:
CHECKPOINTING_INTERVAL_MS = 1000 
CHECKPOINTING_TIMEOUT_MS = 60000 # checkpoints have to complete within one minute, or are discarded

check_config = env.get_checkpoint_config()
check_config.set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
check_config.set_checkpoint_interval(CHECKPOINTING_INTERVAL_MS)
check_config.set_checkpoint_timeout(CHECKPOINTING_TIMEOUT_MS)
check_config.set_max_concurrent_checkpoints(1)
check_config.set_externalized_checkpoint_retention(ExternalizedCheckpointRetention.RETAIN_ON_CANCELLATION) # very important, otherwise nothing would be kept after a docker container rebuild

t_env = StreamTableEnvironment.create(env)


# I wrote this function so I can add the file name without the full absolute path when calling the other function
def computeAbsPath(path: str) -> str:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(SCRIPT_DIR, path)


# Read all queries from a .sql file in the specified path, tokenize them by ; and execute them
def execute_sql_file(t_env, file_path, is_DML: bool):
    with open(file_path, 'r') as f:
        sql = f.read()
        for statement in sql.split(';'):
            if statement.strip():
                if is_DML:        #We add DML statements to the statement set to execute them all at once at the end of this file
                   stmt_set.add_insert_sql(statement)
                else:               #Otherwise, we simply execute DDL statements
                    t_env.execute_sql(statement)
                    

# Creating the statement set for DML statements (DDL statements don't need one).
# We have only one interconnected DAG for the entire pipeline, so we can keep this as a global variable for simplicity.
stmt_set = t_env.create_statement_set()


# Format: (relative path starting from src/flink, statement set)
list_of_paths = [
    ('DDL/DDL_flink_normalization.sql', False),
    ('DML/load_normalization/load_DS1_binance_normalized_stream.sql', True),
    ('DML/load_normalization/load_DS2_mexc_normalized_stream.sql', True),
    ('DML/load_normalization/load_unified_normalized_stream.sql', True),

    ('DDL/derived_metrics/DDL_flink_OHLCV.sql', False)
]

# In this loop, DDL statements will be executed while DML statements will be added to the statement set
for path, is_DML in list_of_paths:
    # print(path, stmt_set_ref)
    execute_sql_file(t_env, file_path=computeAbsPath(path), is_DML=is_DML)


# Execute all DML statements as a named job for future idempotency
print(f"Launching {JOB_NAME}...")
print(env._j_stream_execution_environment.getConfiguration().toMap())
result = stmt_set.execute()
print(result.get_job_client())