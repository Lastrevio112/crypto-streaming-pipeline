import os
import json
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from websocket import ABNF
import websocket
import threading

# Imports created by me
from src.kafka_producers import WebSocketProducer, custom_partitioner

class BinanceProducer_DS1(WebSocketProducer):
    def __init__(self, url, streams, producer, topic, schema_registry_url):
        super().__init__(url, streams, producer, topic)

        schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

        # Fetch the latest registered schema — if Binance adds fields, we update the registry once and producers pick it up on next restart
        registered = schema_registry_client.get_latest_version(f"{topic}-value")
        schema_str = registered.schema.schema_str

        self.avro_serializer = AvroSerializer(
            schema_registry_client,
            schema_str,
            conf={"auto.register.schemas": False} 
        )
        self.topic = topic
    
    def reset(self):
        self._stop_ping = threading.Event()
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            # This is what we add in the child class:
            on_ping=self.on_ping
        )
    
    # Binance sends a ping frame every 20 seconds - if we don't send a pong frame back within one minute we are disconnected.
    def on_ping(self, ws, message):
        ws.send(message, opcode=ABNF.OPCODE_PONG)
        print(f"Received Ping, sent Pong with payload: {message}")
    
    def on_message(self, ws, message):
        data = json.loads(message)
        # subscription response looks like {"result": null, "id": 1}
        if "result" in data:
            if data["result"] is None:
                print(f"Subscription confirmed (id={data['id']})")
            else:
                print(f"Subscription failed: {data}")
            return
        
        # Binance warns 10 minutes before 24h disconnection
        if data.get("e") == "serverShutdown":
            print("serverShutdown received, closing connection for reconnect...")
            ws.close()
            return
        
        # If data is corrupt, don't send it downstream. Certain fields are mandatory.
        if any(data[x] is None for x in ("T", "s", "t", "p")):
            return
        if data["p"] == 0 or data["p"] == "0":
            return

        symbol = data.get("s")  # we get the cryptocurrency here, which is also the partition key
        partition = custom_partitioner(symbol, num_partitions=int(os.getenv("NUM_PARTITIONS")))

        serialized = self.avro_serializer(
            data,
            SerializationContext(self.topic, MessageField.VALUE)
        )
        
        # otherwise it's actual market data — produce to Kafka
        self.producer.produce(
            self.topic,
            key=symbol,
            value=serialized,
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
    
    # Overriding parent class in order to send pings to Binance. For MEXC this is not needed as we have a customized ping mechanism.
    def run(self):
        self.ws.run_forever(ping_interval=20, ping_timeout=10)
    