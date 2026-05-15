""" A websocket our front end can connect to that gives all incoming trades from unified_normalized_stream with the coin_symbol as an API endpoint."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from aiokafka import AIOKafkaConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import os
import json
import uuid

app = FastAPI()

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
SCHEMA_REGISTRY_URL = "http://schema-registry:8081"
TOPIC_NAME = "unified_normalized_stream"

# Allowed list of symbols
ALLOWED_SYMBOLS = set()
with open(str(os.environ.get("TOP_50_COINS_FILE_PATH")), "r") as f:
    data = json.load(f)
    for symbol in data["symbols"]:
        ALLOWED_SYMBOLS.add(symbol)

# Initialize Schema Registry and Avro Deserializer
sr_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
avro_deserializer = AvroDeserializer(sr_client, schema_str=None)

# Thread pool executor to offload the synchronous CPU-bound Avro deserialization
executor = ThreadPoolExecutor(max_workers=4)

"""Synchronous helper functions to decode Avro bytes."""
def deserialize_avro_value(data):
    if data is None:
        return None
    ctx = SerializationContext(TOPIC_NAME, MessageField.VALUE)
    return avro_deserializer(data, ctx)

def deserialize_avro_key(data):
    if data is None:
        return None
    ctx = SerializationContext(TOPIC_NAME, MessageField.KEY)
    return avro_deserializer(data, ctx)

@app.websocket("/ws/trades/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    # Validate the symbol parameter immediately
    if symbol not in ALLOWED_SYMBOLS:
        await websocket.close(code=4000, reason="Invalid symbol")
        return

    await websocket.accept()

    # Generate a unique group_id for every single WebSocket connection
    unique_group_id = f"websocket-consumer-{symbol}-{uuid.uuid4()}"
    
    # Initialize a dedicated Kafka consumer per WebSocket connection for isolated filtering
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        group_id=unique_group_id,
        enable_auto_commit=True
    )
    
    await consumer.start()
    print(f"Kafka consumer started for group: {unique_group_id}")
    
    try:
        # Loop over the incoming Kafka stream asynchronously
        async for msg in consumer:
            # Safely parse the Avro value using a threadpool to prevent event loop lag
            loop = asyncio.get_running_loop()
            parsed_value = await loop.run_in_executor(executor, deserialize_avro_value, msg.value)
            parsed_key = await loop.run_in_executor(executor, deserialize_avro_key, msg.key)
            
            if parsed_value is None:
                continue

            actual_key = parsed_key
            if isinstance(parsed_key, dict):
                actual_key = parsed_key.get("coin_symbol")

            print(f"[DEBUG] Key Data: {parsed_key} | Value Data: {parsed_value}", flush=True)
            
            if actual_key == symbol:
                await websocket.send_json(parsed_value)
                
    except WebSocketDisconnect:
        print(f"Client disconnected from channel: {symbol}")
    except Exception as e:
        print(f"Error handling streaming for {symbol}: {e}")
    finally:
        await consumer.stop()   # Clean up resources