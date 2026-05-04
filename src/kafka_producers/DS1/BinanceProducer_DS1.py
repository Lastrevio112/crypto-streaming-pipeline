from src.kafka_producers import WebSocketProducer
import json
from custom_partitioner import custom_partitioner
import os

class BinanceProducer_DS1(WebSocketProducer):
    def on_message(self, ws, message):
        data = json.loads(message)
        # subscription response looks like {"result": null, "id": 1}
        if "result" in data:
            if data["result"] is None:
                print(f"Subscription confirmed (id={data['id']})")
            else:
                print(f"Subscription failed: {data}")
            return

        symbol = data.get("s")  # we get the cryptocurrency here, which is also the partition key
        partition = custom_partitioner(symbol, num_partitions=int(os.getenv("NUM_PARTITIONS")))
        
        # otherwise it's actual market data — produce to Kafka
        self.producer.produce(
            self.topic,
            key=symbol,
            value=message,
            partition=partition,
        )
        self.producer.poll(0)

    def on_open(self, ws):
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": self.streams,
            "id": 1
        }
        ws.send(json.dumps(subscribe_message))
        print("Connected and subscription sent to Binance DS1 stream.")