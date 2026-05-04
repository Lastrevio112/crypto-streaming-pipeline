from src.kafka_producers import WebSocketProducer
import json

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
        
        # otherwise it's actual market data — produce to Kafka
        self.producer.produce(self.topic, value=message)
        self.producer.poll(0)

    def on_open(self, ws):
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": self.streams,
            "id": 1
        }
        ws.send(json.dumps(subscribe_message))
        print("Connected and subscription sent to Binance DS1 stream.")