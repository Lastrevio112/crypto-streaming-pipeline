""" This code should run only once in order to register the AVRO schema in the schema registry for data source 2 (MEXC). """
""" Documentation for the schema fields can be found here: https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#trade-streams"""

import os
from src.kafka_schema_registry.register_schema import register_schema

SCHEMA_REGISTRY_URL = str(os.environ.get("SCHEMA_REGISTRY_URL"))
SUBJECT = "mexc_ds2_trades-value"

schema = {
    "type": "record",
    "name": "MexcTrade",
    "namespace": "com.mexc.trades",
    "fields": [
        {"name": "channel", "type": "string"},
        {"name": "symbol", "type": "string"},
        {"name": "sendtime", "type": "long"},
        {
            "name": "publicdeals",
            "type": {
                "type": "record",
                "name": "PublicDeals",
                "fields": [
                    {"name": "eventtype", "type": "string"},
                    {
                        "name": "dealsList",
                        "type": {
                            "type": "array",
                            "items": {
                                "type": "record",
                                "name": "Deal",
                                "fields": [
                                    {"name": "price", "type": "string"},
                                    {"name": "quantity", "type": "string"},
                                    {"name": "tradetype", "type": "int"},
                                    {"name": "time", "type": "long"},
                                ]
                            }
                        }
                    }
                ]
            }
        }
    ]
} # I get Yandere Simulator code flashbacks every time I look at this schema, ngl

if __name__ == "__main__":
    schema_id = register_schema(SCHEMA_REGISTRY_URL, SUBJECT, schema, "AVRO", "FORWARD")
    print(f"Schema registered with ID: {schema_id}")