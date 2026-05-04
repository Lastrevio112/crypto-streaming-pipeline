from confluent_kafka import Producer
import json
import os
import threading
import time

from MexcProducer_DS2 import MexcProducer_DS2

def run_with_reconnect(producer, interval_hours=23):
    while True:
        t = threading.Thread(target=producer.run, daemon=True)
        t.start()
        time.sleep(interval_hours * 3600)
        producer.stop()  
        print(f"Reconnecting after {interval_hours}h...")

if __name__ == "__main__":
    BOOTSTRAP = "kafka:9092"
    TOPIC = str(os.getenv("TOPIC_DS_2"))
    URL_TO_MEXC = "wss://wbs-api.mexc.com/ws"
    SCHEMA_REGISTRY_URL = str(os.environ.get("SCHEMA_REGISTRY_URL"))

    producer = Producer({"bootstrap.servers": BOOTSTRAP})

    list_of_lists_of_streams = [[], []] # MEXC allows max 30 streams per connection, we have 50 coins, we split in two connections
    with open(str(os.environ.get("TOP_50_COINS_FILE_PATH")), "r") as f:
        data = json.load(f)
        symbols = data["symbols"]
        mid = len(symbols) // 2
        list_of_lists_of_streams = [symbols[:mid], symbols[mid:]]
    
    mexc_producer_1 = MexcProducer_DS2(URL_TO_MEXC, list_of_lists_of_streams[0], producer, TOPIC, SCHEMA_REGISTRY_URL)
    mexc_producer_2 = MexcProducer_DS2(URL_TO_MEXC, list_of_lists_of_streams[1], producer, TOPIC, SCHEMA_REGISTRY_URL)

    # We need both producers to run concurrently so we need multi-threading:
    t1 = threading.Thread(target=run_with_reconnect, args=(mexc_producer_1,), daemon=True)
    t2 = threading.Thread(target=run_with_reconnect, args=(mexc_producer_2,), daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()