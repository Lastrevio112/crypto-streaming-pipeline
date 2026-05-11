import os
import json
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

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

    def on_message(self, ws, message):
        data = json.loads(message)
        # subscription response looks like {"result": null, "id": 1}
        if "result" in data:
            if data["result"] is None:
                print(f"Subscription confirmed (id={data['id']})")
            else:
                print(f"Subscription failed: {data}")
            return
        
        # Handle Binance application-level ping
        if "ping" in data:
            ws.send(json.dumps({"pong": data["ping"]}))
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
    