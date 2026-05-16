# Real-time Cryptocurrency Charting Platform
This is a near real time (2-5s of latency end to end) streaming pipeline using Kafka, Flink, Clickhouse, Grafana, Docker and Python/Javascript/Java/SQL. 

This project attempted to do something similar to what websites like Tradeview do, by streaming data from two websockets (Binance and MEXC) in real time using Kafka and creating trading-relevant aggregate measures on various candles using Flink - all of this being dumped in a Clickhouse sink at the end for fast OLAP processing. 

Grafana connects to Clickhouse directly and is embedded in the HTML of the front-end built with vanilla Javascript. Full stack was containarized in Docker on a free Oracle virtual machine.

**YOU CAN VIEW THE PROJECT HERE:** https://lastrevioprojects.org/index.html

# DATA FLOW UNTIL NOW

<img width="1569" height="1078" alt="Data Flow" src="https://github.com/user-attachments/assets/4bf93b43-64e0-4d25-a9bc-d535737264a0" />

# KAFKA PRODUCERS DOCUMENTATION

Under src/kafka_producers there is all the source code for the producers of this pipeline writing to Kafka:
```
src/
├── kafka_producers/
│   ├── DS1/
│   │   ├── BinanceProducer_DS1.py
│   │   ├── run_DS1_producer.py
│   ├── DS2/
│   │   ├── MexcProducer_DS2.py
│   │   ├── run_DS2_producer.py
│   ├── __init__.py
│   ├── custom_partitioner.py
│   ├── run_with_reconnect.py
│   └── WebSocketProducer.py
├── kafka_schema_registry/
│   ├── register_schema_DS1.py
│   ├── register_schema_DS2.py
│   └── register_schema.py
├── serialized_data/
│   └── top_50_coins.json
└── kafka_topic_create_commands.txt
```

We have two data sources: the public Binance websocket (data source 1) and the MEXC websocket (data source 2). These websockets give real-time feeds of cryptocurrency trades happening on their platform.

We extract around 50 cryptocurrencies from each websocket: they are stored in a JSON file under src/serialized_data.

Each data source corresponds to a separate Kafka topic. Each Kafka topic has 10 partitions. Five of the cryptocurrencies with the most traffic (ETHUSDT, BTCUSDT, SUIUSDT, SOLUSDT, CHIPUSDT) each get their own partition.
The other 45 coins are split evenly between the remaining 5 partitions based on a hash key + modulo.

The custom partitioner lives in src/kafka_producers/custom_partitioner.py.

Each data source has its own sub-folder: DS1, DS2. In each data source folder we have a class (ex: BinanceProducer_DS1.py) and a script that runs the producer based on the implementation of that class (ex: run_DS1_producer.py).

Each of the two classes inherits from a parent class called WebSocketProducer which lives in the WebSockerProducer.py file. This class implements the generic "Kafka producer that takes data from a websocket" architecture. 

It implements the on_error, on_close, run and stop methods, since these are the same for all data sources. It also implements a reset method, used in the constructor as well as in the run_with_reconnect() method. Finally, it implements a ping_pong() method, used in the run() override of its child classes - this is because the websockets disconnect you after a certain number of seconds of inactivity.

on_message and on_open are _abstract methods_ in this class since they need to be implemented in a different way by each child class (i.e.: by each data source).

run_with_reconnect.py is a file that implements the run_with_reconnect function that is used by both data sources - this is because a websocket connection is only valid for a certain period of time, after which we have to disconnect and reconnect.

The Binance Producer (DS1) was simpler to implement: on each message, it checks whether it's a subscription confirmed message and acts accordingly, and if not, it produces to its corresponding Kafka topic.
On opening, it sends the corresponding subscription message.

The MEXC Producer (DS2) was trickier as it sends the data in protobuf format instead of JSON, which had to be deseriailized.

The run_ds2_producer.py script was also trickier than the one from data source 1. This is because the MEXC websocket had one more  constraint: you can only subscribe to 30 streams at once, but I had 50 coins. Because of this, I had to split the 50 coins into two halves, each processed by a separate producer in parallel using multi-threading.

Lastly, we have one AVRO schema_registry with _forward compatibility_ to make sure that if the websockets add fields or something, our pipeline doesn't break.
Under src/kafka_schema_registry we have a generic function to register any schema (register_schema.py) and two scripts that run it for each data source.

The Kafka topics have a replication-factor of 1 - this is because I am running this on a single broker (an Oracle VM) so it would be pointless to replicate data.

# FLINK DOCUMENTATION

The cleaning of our data, as well as the calculation of our 'business metrics' over certain time windows (vwap, standard deviation of price, other things that might be relevant to crypto traders) was done with **Flink SQL**. At the same time, in the src/flink/ sub-folder, there is also Python and Java code. 

**Folder structure**

The folder structure for our Flink code is like this: 
```
src/
└── flink/
    ├── DDL/
    │   ├── DDL_flink_normalization.sql
    │   └── DDL_flink_OHLCV.sql
    ├── DML/
    │   ├── load_derived_metrics/
    │   │   └── load_derived_ohlcv.sql
    │   └── load_normalization/
    │       ├── load_DS1_binance_normalized_stream.sql
    │       ├── load_DS2_mexc_normalized_stream.sql
    │       └── load_unified_normalized_stream.sql
    ├── partitioners/
    │   └── SymbolPartitioner.java
    └── UDAFs/
        ├── first_and_last_value/
        │   ├── Accumulator.java
        │   ├── BoundaryValueAggFunction.java
        │   ├── FirstValueAggFunction.java
        │   └── LastValueAggFunction.java
        └── safe_stddev_pop/
            ├── StdDevAccumulator.java
            └── StdDevPopAggFunction.java
execute_all_sql_files.py
run_flink_from_checkpoint.sh
```
-The main orchestrator script that configures and runs our entire pipeline/DAG was written in Python (PyFlink) and it lives in src/flink/execute_all_sql_files.sql.

-Custom UDAFs were written in Java that re-implement standard Flink functions if they were buggy or limited in some way - these live src/flink/UDAFs.

-The custom partitioner our Kafka producers use upstream was re-written in Java as well so that it can be used by the Flink SQL DDL statements - this Java class lives in src/flink/partitioners/SymbolPartitioner.java. 

-_run_flink_from_checkpoint.sh_ -> this is a bash script that runs our main PyFlink orchestrator from the last checkpoint after crawling our 'checkpoints' named Docker volume. It is called on every container rebuild by docker-compose.yml.

-Lastly, we have the .sql files that live in the DDL and DML sub-folders.

**PyFlink orchestrator - execute_all_sql_files.py**

The data flow goes like this: each time my Docker container is rebuilt, docker-compose.yml runs as usual and it calls run_flink_from_checkpoint.sh. The beforementioned bash script crawls our checkpoints named volume, finds the latest checkpoint (if there is one, otherwise it starts the script without checkpoint) and runs our PyFlink orchestrator from that checkpoint.

The PyFlink orhcestrator, in turn, runs our .sql files: the DDL files are executed one by one, while the DML statements are all added to one big statement set that is executed at the end -> this is because we have only one interconnected DAG, hence the need for a single statement set. So the execution flow goes like this: docker compose -> bash script -> PyFlink -> .sql files.

Checkpointing: we use at-least-once checkpointing with a checkpoint comitted once per second. This gurantees us low-latency (that we wouldn't have had with exactly once semantics) while also only getting duplicates in case of failures or container rebuilds, and even in those cases, the time frame in which we would get duplicates would never be larger than 1 second. Time out was configured as well: checkpoints have to complete within one minute, or are discarded. VERY IMPORTANTLY, checkpoints are retained on cancellation and are mounted to a named docker volume -> this makes them survive Docker container rebuilds, which I trigger very often in development.

**Flink SQL**

Each SQL table has a Kafka topic underneath as storage, with 10 partitions and a replication factor of 1. The tables live across three layers in the data flow: the first layer are the pure sources, two tables which simply read the raw data from the topics in which our two Kafka producers write into. The second layer consists of topics which act as both sources and sinks - this is the 'normalized' layer which cleans the data, removes unnecessary columns and casts everything to the correct data types. Lastly, we have the "derived" layer which acts only as a sink for Flink and not as a source (although it is a source for Clickhouse, downstream): this computes trading-relevant business metrics accross various time windows - 1 second tumbling, 5 second sliding with 1 second step, 1 minute sliding with 5 second step and 5 minute sliding with 30 second step.

The three layers described above _roughly_ correspond to the bronze, silver and gold layers in a medallion architecture, although it's debatable how much that terminology applies to streaming - especially in my case where the supposed 'gold' layer will still be a source for Clickhouse further downstream, and Clickhouse itself will compute various materialized views with even more business metrics, so maybe Clickhouse is the actual gold layer? Idk.

What is worth noting here that is very important is that the four 'derived' tables use the upsert-kafka connector and therefore could not be partitioned by a custom partitioner class - this is not a problem since it's the normalized (silver?) layer that I actually cared for to be partitioned in the same way our source Kafka topics are (with the custom partitioner). I wanted faster filtering and aggregation per cryptocurrency, which means that only the sources for the Flink tables which do aggregate by coin (that is, the derived layer) needed to be partitioned in that custom way, which is what actually ended up happening, which is good.

Another thing worth noting about the derived tables: I only computed metrics that would be impossible to derive from other metrics accross a time window. This is to keep the data "normalized" to a certain extent, although I'm not sure if you can call it database normalization as that is a batch/RDBMS concept which doesn't apply to me when I don't even have a database so upstream. Nevertheless, what I implemented _kind of_ resembles the equivalent of a 3NF normalization for streams - but with measures instead of dimensions. What I intended to do is not to have a measure in my Flink tables that can be derived from other measures within the same time window. For example, I decided to not add a "net flow" column since this can be easily derived from aggressive_buy_volume - aggressive_sell_volume downstream. Therefore, all metrics which can be derived from the existing metrics will be implemented downstream by Clickhouse materialized views.

A note on UDAFs: I had to re-implement in Java the FIRST_VALUE and LAST_VALUE functions, to compute the open and close price per candle. This is because the built-in Flink functions cannot be used within sliding windows that have a group by. I also had to re-implement the standard deviation function in Java because the built-in one literally had a bug that would crash my pipeline (it would try to convert 'NaN' to DECIMAL for windows with zero trades), no matter how many TRY_CASTs and COALESCEs I would add in SQL.

The custom Java UDAFs were written by extending the AggregateFunction class, writing a custom Accumulator and implementing/overriding the accumulate, merge, retract and getValue methods accordingly. (For what each of those four methods do in Flink Java, please refer to the official Flink documentation [here](https://nightlies.apache.org/flink/flink-docs-stable/api/java/org/apache/flink/table/functions/AggregateFunction.html).)

# CLICKHOUSE DOCUMENTATION

Under src/DDL_src we have 4 .sql files each defining 3 entities: a kafka connector, a materialized view and a final table. For example: kafka_derived_ohlcv_5s_sliding (the connector), mv_src_5s_sliding (the materializied view), src_5s_sliding (the actual table in the database storing the data that we can query from).

The tables starting in "kafka_" are the simply Kafka-Clickhouse connectors that work under the hood as Kafka consumers - they are temporary 'landing zones' of each message, and once a message is 'consumed from the consumer' it disappears from the queue. They cannot be queried directly in Clickhouse.

The materialized views are simply triggers, since they are inserting data into a MergeTree table - their only purpose is to move the data from the kafka consumers to the 'real' tables incrementally. This is one feature of Clickhouse: the incremental materialized view is not like a regular table that is simply refreshed periodically, instead it defines a rule on how to keep data up to date with each trigger, almost like in a CDC kind of way.

Extra business metrics (net_flow, average_trade_size, etc.) were added in the final Analytics layer that Clickhouse queries from. These consist of 'regular' (non-materialized) views. They are separated into tumbling views, each representing a candle that can be selected in the front-end: 1s, 5s, 30s, 1m, 5m, 30m, 1h, 4h, 24h). There are three respective sliding window analytics views as well (corresponding to the three intervals from Flink).

To avoid code duplication, I avoided copy-pasting the same code 9 times, and instead defined in Python a parent/base class called "AnalyticsView" and had two child classes inherit from it (AnalyticsTumbleView and AnalyticsSlidingView) - the base class is an abstract class with the query generator as an abstract method.

The execute_all_sql_files.py script executes all our code: creates tables, materialized views, replaces view definition, etc.

# FRONT END DOCUMENTATION

I am not a web developer, so this might be the weakest part of the project in terms of code quality. Nevertheless, it's functional.

I created four dashboards in Grafana and embedded each chart as an HTML IFrame object with the ?kiosk=true parameter in the URL to make it (mostly) read-only and restrict access to admin features. Since I did not embed the entire dashboard as an IFrame, and instead embedded each chart, the user doesn't have access to the variables I used in Grafana by default (coin and candle size selector) as well as the time range selection. Therefore, I had to create those buttons by scratch in HTML/CSS and use Javascript to create the logic that fires when you press them.

The website also has a cool-looking sidebar that displays when you hover it, with hyperlinks to the other dashboards and my GitHub repository.

# NGINX / REVERSE PROXYING

Grafana has a refresh rate of 2s which means that every 2 seconds, Clickhouse gets queried. This worried me because if 1000 people enter my website at once, I don't want Clickhouse to get queried 1000 at once, I want it to get queried once on the server-side and for the results to be displayed to each client from the cache. The easiest way to achieve this was with nginx. Nginx can cache the actual pixels on the website so that users do not have direct access to make requests to our database. Its cache has a TTL of 2 seconds (the Grafana refresh rate) and its caching the body of the POST request (which is how Grafana makes requests to Clickhouse).

I applied a global rate limit with a burst allowance of 60, as well as a max size of the cache (Both on disk and in RAM) in order to prevent any malicious actors 'trolling' me by making tens of thousands of requests per second. Even if they wouldn not poll my database with those requests, they would fill up the cache with garbage so other users would not be able to load the website - hence they will be blocked.
