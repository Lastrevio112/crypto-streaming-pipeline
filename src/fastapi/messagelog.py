""" A websocket our front end can connect to that gives all incoming trades from unified_normalized_stream with the coin_symbol as an API endpoint."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from aiokafka import AIOKafkaConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import os
import json

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
avro_deserializer = AvroDeserializer(sr_client)

# Thread pool executor to offload the synchronous CPU-bound Avro deserialization
executor = ThreadPoolExecutor(max_workers=4)

def deserialize_avro(data):
    """Synchronous helper function to decode Avro bytes."""
    if data is None:
        return None
    # Context is None here because schema is implicitly linked within the payload
    return avro_deserializer(data, context=None)

@app.websocket("/ws/trades/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    # Validate the symbol parameter immediately
    if symbol not in ALLOWED_SYMBOLS:
        await websocket.close(code=4000, reason="Invalid symbol")
        return

    await websocket.accept()
    
    # Initialize a dedicated Kafka consumer per WebSocket connection for isolated filtering
    consumer = AIOKafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="latest" # Matches your Flink configuration
    )
    
    await consumer.start()
    
    try:
        # Loop over the incoming Kafka stream asynchronously
        async for msg in consumer:
            # Safely parse the Avro value using a threadpool to prevent event loop lag
            loop = asyncio.get_running_loop()
            parsed_value = await loop.run_in_executor(executor, deserialize_avro, msg.value)
            
            if parsed_value is None:
                continue
            
            # Extract symbol and check against endpoint path parameter
            coin_symbol = parsed_value.get("coin_symbol")
            
            if coin_symbol == symbol:
                await websocket.send_json(parsed_value)
                
    except WebSocketDisconnect:
        print(f"Client disconnected from channel: {symbol}")
    except Exception as e:
        print(f"Error handling streaming for {symbol}: {e}")
    finally:
        await consumer.stop()   # Clean up resources