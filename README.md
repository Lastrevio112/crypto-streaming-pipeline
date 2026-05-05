# Real-time Cryptocurrency Price Analysis
This is an in-progress streaming pipeline using Kafka, Flink, FastAPI, Javascript, Clickhouse and Docker.

# KAFKA PRODUCERS DOCUMENTATION

Under src/kafka_producers there is all the source code for the producers of this pipeline writing to Kafka.

We have two data sources: the public Binance websocket (data source 1) and the MEXC websocket (data source 2). These websockets give real-time feeds of cryptocurrency trades happening on their platform.

We extract around 50 cryptocurrencies from each websocket: they are stored in a JSON file under src/serialized_data.

Each data source corresponds to a separate Kafka topic. Each Kafka topic has 10 partitions. Five of the cryptocurrencies with the most traffic (BABYUSDT, ETHUSDT, MEGAUSDT, CHIPUSDT, BTCUSDT) each get their own partition.
The other 45 coins are split evenly between the remaining 5 partitions based on a hash key + modulo.

The custom partitioner lives in src/kafka_producers/custom_partitioner.py.

Each data source has its own sub-folder: DS1, DS2. In each data source folder we have a class (ex: BinanceProducer_DS1.py) and a script that runs the producer based on the implementation of that class (ex: run_DS1_producer.py).

Each of the two classes inherits from a parent class called WebSocketProducer which lives in the WebSockerProducer.py file. This class implements the generic "Kafka producer that takes data from a websocket" architecture. 
It implements the on_error, on_close, run and stop methods, since these are the same for all data sources. 
on_message and on_open are _abstract methods_ in this class since they need to be implemented in a different way by each child class (i.e.: by each data source).

The Binance Producer (DS1) was simpler to implement: on each message, it checks whether it's a subscription confirmed message and acts accordingly, and if not, it produces to its corresponding Kafka topic.
On opening, it sends the corresponding subscription message.

The MEXC Producer (DS2) was trickier as it sends the data in protobuf format instead of JSON, which had to be deseriailized.

The run_ds2_producer.py script was also trickier than the one from data source 1. This is because the MEXC websocket had two constraints: firstly, you can only subscribe to 30 streams at once, but I had 50 coins. 
Secondly, a subscription cannot last longer than 24 hours.

Because of this, I had to implement a custom function to reconnect every 23 hours and I also had to split the 50 coins into two halves, each processed by a separate producer in parallel using multi-threading.

Lastly, we have one AVRO schema_registry with _forward compatibility_ to make sure that if the websockets add fields or something, our pipeline doesn't break.
Under src/kafka_schema_registry we have a generic function to register any schema (register_schema.py) and two scripts that run it for each data source.
