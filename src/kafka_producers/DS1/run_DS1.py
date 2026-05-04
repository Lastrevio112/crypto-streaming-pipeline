from BinanceProducer_DS1 import BinanceProducer_DS1
from confluent_kafka import Producer
import json
from custom_partitioner import custom_partitioner
import os

if __name__ == "__main__":
    BOOTSTRAP = "kafka:9092"
    TOPIC = str(os.getenv("TOPIC_DS_1"))
    URL_TO_BINANCE = "wss://stream.binance.com:9443/ws"

    producer = Producer({"bootstrap.servers": BOOTSTRAP})
    streams = []
    with open("/workspace/src/serialized_data/top_50_coins.json", "r") as f:
        data = json.load(f)
        streams = [s.lower() + "@trade" for s in data["symbols"]]
    
    binance_producer = BinanceProducer_DS1(URL_TO_BINANCE, streams, producer, TOPIC)
    binance_producer.run()