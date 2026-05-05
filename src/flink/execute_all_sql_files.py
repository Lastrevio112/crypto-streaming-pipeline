from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
import os

# Setup
env = StreamExecutionEnvironment.get_execution_environment()

# Table environment
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, settings)

# I wrote this function so I can add the file name without the full absolute path when calling the other function
def computePath(path = str) -> str:
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
                    print("=== EXECUTING ===")
                    print(statement)
                    t_env.execute_sql(statement)

stmt_set = t_env.create_statement_set()

execute_sql_file(t_env, computePath('DDL_flink_normalization.sql'), stmt_set=None)
#print(t_env.list_tables())

# Submit all DML statements as one Flink job here:
#stmt_set.execute()