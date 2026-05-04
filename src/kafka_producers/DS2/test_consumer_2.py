from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import os

consumer = Consumer({
    "bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
    "group.id": "test-consumer-2",
    "auto.offset.reset": "earliest"
})

schema_registry_client = SchemaRegistryClient({"url": os.environ.get("SCHEMA_REGISTRY_URL")})
avro_deserializer = AvroDeserializer(schema_registry_client)

consumer.subscribe([str(os.environ.get("TOPIC_DS_2"))])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue
        data = avro_deserializer(msg.value(), SerializationContext(str(os.environ.get("TOPIC_DS_2")), MessageField.VALUE))
        for deal in data["dealsList"]: # (1: Buy, 2: Sell)
            if deal["tradetype"] == 1:
                print(f"{data['symbol']} was bought at price {deal['price']} with quantity {deal['quantity']}")
            else:
                print(f"{data['symbol']} was sold at price {deal['price']} with quantity {deal['quantity']}")
        
finally:
    consumer.close()