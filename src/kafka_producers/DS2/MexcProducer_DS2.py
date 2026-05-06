import os, sys
import json
import threading
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

sys.path.append('/workspace/src/proto')

from src.proto import PushDataV3ApiWrapper_pb2
# Imports created by me
from src.kafka_producers import WebSocketProducer, custom_partitioner

class MexcProducer_DS2(WebSocketProducer):
    def __init__(self, url, streams, producer, topic, schema_registry_url, no_of_ms=100, ping_interval_seconds=50):
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
        self.no_of_ms = no_of_ms # MEXC makes us choose between 10ms and 100ms latency, we choose 100ms by default
        self.ping_interval_seconds = ping_interval_seconds
    
    def on_message(self, ws, message):
        # subscription response looks like {"id": 0, "code": 0, "msg": "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"}
        if isinstance(message, str):
            data = json.loads(message)
            if "code" in data:
                if data["code"] == 0 and data["msg"] != "PONG":
                    print(f"Subscription confirmed (id={data['id']})")
                elif data["code"] == 0 and data["msg"] == "PONG":
                    print(f"Ping has been responded with PONG for id {data['id']}.")
                else:
                    print(f"Subscription failed: {data}")
            return

        # Binary = protobuf trade data
        wrapper = PushDataV3ApiWrapper_pb2.PushDataV3ApiWrapper()
        try:
            wrapper.ParseFromString(message)
        except Exception as e:
            print(f"Protobuf parse error: {e}")
            return

        symbol = wrapper.symbol
        partition = custom_partitioner(symbol, num_partitions=int(os.getenv("NUM_PARTITIONS")))

        # Converting to plain dict to match my Avro schema
        data = {
            "channel": wrapper.channel,
            "symbol": symbol,
            "sendtime": wrapper.sendTime,
            "publicdeals": {
                "eventtype": wrapper.publicAggreDeals.eventType,
                "dealsList": [
                    {
                        "price": deal.price,
                        "quantity": deal.quantity,
                        "tradetype": deal.tradeType,
                        "time": deal.time,
                    }
                    for deal in wrapper.publicAggreDeals.deals
                ]
            }
        }

        serialized = self.avro_serializer(
            data,
            SerializationContext(self.topic, MessageField.VALUE)
        )

        # Produce to Kafka:
        self.producer.produce(
            self.topic,
            key=symbol,
            value=serialized,
            partition=partition,
        )
        self.producer.poll(0)
    
    def on_open(self, ws):
        params = []

        #MEXC API requires a list of parameters where each crypto coin is prefixed with that string
        for stream in self.streams:
            params.append(f"spot@public.aggre.deals.v3.api.pb@{self.no_of_ms}ms@{stream}")

        subscribe_message = {
            "method": "SUBSCRIPTION",
            "params": params
        }

        ws.send(json.dumps(subscribe_message))
        print("Connected and subscription sent to MEXC DS2 stream.")
    
    # Overriding the base class's run method in order to send a ping message every 50 seconds, as MEXC websocket times out after 60 seconds of inactivity.
    def run(self):
        self._stop_ping = threading.Event()
    
        def ping_loop():
            while not self._stop_ping.wait(self.ping_interval_seconds):  # wait returns True if set, False on timeout
                try:
                    self.ws.send(json.dumps({"method": "PING"}))
                except Exception as e:
                    print(f"Ping failed: {e}")
                    break

        ping_thread = threading.Thread(target=ping_loop, daemon=True)
        ping_thread.start()

        try:
            super().run()
        finally:
            self._stop_ping.set()