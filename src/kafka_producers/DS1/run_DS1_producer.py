from confluent_kafka import Producer
import json
import os, sys

sys.path.append('/workspace/src/kafka_producers')

from BinanceProducer_DS1 import BinanceProducer_DS1
from run_with_reconnect import run_with_reconnect

if __name__ == "__main__":
    BOOTSTRAP = "kafka:9092"
    TOPIC = str(os.getenv("TOPIC_DS_1"))
    URL_TO_BINANCE = "wss://stream.binance.com:9443/ws"
    SCHEMA_REGISTRY_URL = str(os.environ.get("SCHEMA_REGISTRY_URL"))

    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    streams = []
    with open(str(os.environ.get("TOP_50_COINS_FILE_PATH")), "r") as f:
        data = json.load(f)
        streams = [s.lower() + "@trade" for s in data["symbols"]]
    
    binance_producer = BinanceProducer_DS1(URL_TO_BINANCE, streams, producer, TOPIC, SCHEMA_REGISTRY_URL)
    run_with_reconnect(binance_producer)