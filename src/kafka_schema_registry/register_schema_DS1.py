""" This code should run only once in order to register the AVRO schema in the schema registry for data source 1. """

import os
from src.kafka_schema_registry.register_schema import register_schema

SCHEMA_REGISTRY_URL = str(os.environ.get("SCHEMA_REGISTRY_URL"))
SUBJECT = "binance_ds1_trades-value"

schema = {
    "type": "record",
    "name": "BinanceTrade",
    "namespace": "com.binance.trades",
    "fields": [
        {"name": "e", "type": "string"},                          # event type
        {"name": "E", "type": "long"},                            # event time
        {"name": "s", "type": "string"},                          # symbol
        {"name": "t", "type": "long"},                            # trade ID
        {"name": "p", "type": "string"},                          # price
        {"name": "q", "type": "string"},                          # quantity
        {"name": "T", "type": "long"},                            # trade time
        {"name": "m", "type": "boolean"},                         # is buyer market maker
        {"name": "M", "type": ["null", "boolean"], "default": None} # ignore — Binance internal
    ]
}

if __name__ == "__main__":
    schema_id = register_schema(SCHEMA_REGISTRY_URL, SUBJECT, schema, "AVRO", "FORWARD")
    print(f"Schema registered with ID: {schema_id}")