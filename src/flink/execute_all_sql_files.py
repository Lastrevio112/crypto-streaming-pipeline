from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.state_backend import EmbeddedRocksDBStateBackend
from pyflink.table import StreamTableEnvironment, EnvironmentSettings

# Setup
env = StreamExecutionEnvironment.get_execution_environment()

# RocksDB state backend
backend = EmbeddedRocksDBStateBackend()
env.set_state_backend(backend)

# Table environment
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
t_env = StreamTableEnvironment.create(env, settings)

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