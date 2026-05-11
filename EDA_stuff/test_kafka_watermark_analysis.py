from confluent_kafka import Consumer, KafkaException, TopicPartition
from datetime import datetime, timezone, timedelta
import io, fastavro, requests, struct, time
import statistics

SR_URL = "http://schema-registry:8081"
BOOTSTRAP = "kafka:9092"
TOPIC = "unified_normalized_stream"

def get_schema(schema_id):
    r = requests.get(f"{SR_URL}/schemas/ids/{schema_id}")
    return fastavro.parse_schema(r.json()["schema"] if isinstance(r.json()["schema"], dict) 
                                  else __import__('json').loads(r.json()["schema"]))

consumer = Consumer({
    "bootstrap.servers": BOOTSTRAP,
    "group.id": "latency-adhoc-test",
    "auto.offset.reset": "latest"
})

# --- seek to 5 hours ago ---
target_ts_ms = int((datetime.now(timezone.utc) - timedelta(hours=5)).timestamp() * 1000)

# need partition metadata first; assign() requires explicit partitions
metadata = consumer.list_topics(TOPIC)
partitions = [
    TopicPartition(TOPIC, p, target_ts_ms)
    for p in metadata.topics[TOPIC].partitions.keys()
]

offsets = consumer.offsets_for_times(partitions, timeout=10)

# assign (not subscribe) with the resolved offsets
consumer.assign(offsets)
# ---

schemas = {}
lags = []

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        raw = msg.value()
        schema_id = struct.unpack(">I", raw[1:5])[0]
        if schema_id not in schemas:
            schemas[schema_id] = get_schema(schema_id)

        record = fastavro.schemaless_reader(io.BytesIO(raw[5:]), schemas[schema_id])
        
        trade_time_ms = record["trade_time"].timestamp() * 1000
        _, kafka_ts_ms = msg.timestamp()
        
        lag_ms = kafka_ts_ms - trade_time_ms
        lags.append(lag_ms)

        if len(lags) % 1000 == 0:
            lags_sorted = sorted(lags)
            n = len(lags_sorted)
            p = lambda pct: lags_sorted[int(n * pct)]
            print(
                f"n={n} | "
                f"avg={sum(lags)/n:.1f}ms | "
                f"p50={p(0.50):.1f}ms | "
                f"p90={p(0.90):.1f}ms | "
                f"p95={p(0.95):.1f}ms | "
                f"p99={p(0.99):.1f}ms | "
                f"p999={p(0.999) if n >= 1000 else float('nan'):.1f}ms | "
                f"max={max(lags):.1f}ms"
            )

except KeyboardInterrupt:
    if lags:
        lags_sorted = sorted(lags)
        n = len(lags_sorted)
        p = lambda pct: lags_sorted[int(n * pct)]
        print(f"\nFinal ({n} messages):")
        print(f"  avg={sum(lags)/n:.1f}ms")
        print(f"  p50={p(0.50):.1f}ms")
        print(f"  p90={p(0.90):.1f}ms")
        print(f"  p95={p(0.95):.1f}ms")
        print(f"  p99={p(0.99):.1f}ms")
        print(f"  p999={p(0.999) if n >= 1000 else float('nan'):.1f}ms")
        print(f"  max={max(lags):.1f}ms")
finally:
    consumer.close()