from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.common import Configuration
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

env = StreamExecutionEnvironment.get_execution_environment(config)
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, settings)


#Finds the running job by name, triggers savepoint, and cancels it.
def get_savepoint_and_terminate():
    try:
        jobs = requests.get(f"{FLINK_REST}/jobs").json()['jobs']
        running_jobs = [j for j in jobs if j['name'] == JOB_NAME and j['status'] == 'RUNNING']
        
        if not running_jobs:
            return None

        job_id = running_jobs[0]['id']
        print(f"Found running job {job_id}. Triggering savepoint and stopping...")
        
        # Trigger stop with savepoint
        payload = {"targetDirectory": SAVEPOINT_DIR, "drain": True}
        trigger = requests.post(f"{FLINK_REST}/jobs/{job_id}/stop", json=payload).json()
        trigger_id = trigger['request-id']

        # Poll for completion
        while True:
            status = requests.get(f"{FLINK_REST}/jobs/{job_id}/savepoints/{trigger_id}").json()
            if status['status']['id'] == 'COMPLETED':
                return status['operation']['location']
            time.sleep(2)
    except Exception as e:
        print(f"No existing job found or error connecting: {e}")
        return None
    

# I wrote this function so I can add the file name without the full absolute path when calling the other function
def computeAbsPath(path: str) -> str:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(SCRIPT_DIR, path)


# Read all queries from a .sql file in the specified path, tokenize them by ; and execute them
def execute_sql_file(t_env, file_path, stmt_set=None):
    with open(file_path, 'r') as f:
        sql = f.read()
        for statement in sql.split(';'):
            if statement.strip():
                if stmt_set:        #We add DML statements to the statement set to execute them all at once at the end of this file
                    stmt_set.add_insert_sql(statement)
                else:               #Otherwise, we simply execute DDL statements
                    t_env.execute_sql(statement)
                    

# Clean up existing jobs and get state
last_savepoint = get_savepoint_and_terminate()

# Creating the statement set for DML statements (DDL don't need one)
stmt_set = t_env.create_statement_set()


# Format: (relative path starting from src/flink, statement set)
list_of_paths = [
    ('DDL/DDL_flink_normalization.sql', None),
    ('DML/load_normalization/load_DS1_binance_normalized_stream.sql', stmt_set),
    ('DML/load_normalization/load_DS2_mexc_normalized_stream.sql', stmt_set),
    ('DML/load_normalization/load_unified_normalized_stream.sql', stmt_set)
]

# In this loop, DDL statements will be executed while DML statements will be added to the statement set
for path, stmt_set_ref in list_of_paths:
    # print(path, stmt_set_ref)
    execute_sql_file(t_env, computeAbsPath(path), stmt_set=stmt_set_ref)


# Resume from savepoint or start fresh if there isn't one
if last_savepoint:
    print(f"Resuming from: {last_savepoint}")
    t_env.get_config().get_configuration().set_string("execution.savepoint.path", last_savepoint)

# Execute all DML statements as a named job for future idempotency
print(f"Launching {JOB_NAME}...")
result = stmt_set.execute()
print(result.get_job_client())