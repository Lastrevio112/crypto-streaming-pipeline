""" This code should run only once in order to register the AVRO schema in the schema registry for data source 1. """

import requests
import json
import os

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

# Set compatibility to FORWARD
requests.put(
    f"{SCHEMA_REGISTRY_URL}/config/{SUBJECT}",
    json={"compatibility": "FORWARD"}
)

# Register the schema
response = requests.post(
    f"{SCHEMA_REGISTRY_URL}/subjects/{SUBJECT}/versions",
    json={"schema": json.dumps(schema)},
    headers={"Content-Type": "application/vnd.schemaregistry.v1+json"}
)
print(response.json())