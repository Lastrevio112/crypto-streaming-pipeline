// We need the Kafka topics that act as Flink's sinks to be partitioned in the same way that the two sources are partitioned by custom_partitioner.py.
// Since Flink SQL cannot accept Python UDFs in the PARTITIONED BY clause of DDL statements, we had to do this in Java.

package com.crypto.partitioners;

import org.apache.flink.connector.kafka.sink.KafkaPartitioner;
import java.security.MessageDigest;
import java.util.Map;
import java.math.BigInteger;

public class SymbolPartitioner implements KafkaPartitioner<Object>  {

    private static final Map<String, Integer> PARTITION_MAP = Map.of(
        "BABYUSDT", 0,
        "ETHUSDT",  1,
        "MEGAUSDT", 2,
        "CHIPUSDT", 3,
        "BTCUSDT",  4
    );
    private static final int FALLBACK_START = 5;

    @Override
    public int partition(Object record, byte[] key, byte[] value, String targetTopic, int[] partitions) {
        String symbol;
        if (key != null) {
            symbol = new String(key);
        } 
        else {
            symbol = "";
        }

        //If it's one of the five cryptocurrencies, return the key of the dictionary:
        if (PARTITION_MAP.containsKey(symbol)) {
            return PARTITION_MAP.get(symbol);
        }

        //else, hash it between the remaining five partitions:
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hashBytes = md.digest(symbol.getBytes("UTF-8"));
            // Replicate Python's int.from_bytes(hash_bytes, 'big') unsigned
            BigInteger hashInt = new BigInteger(1, hashBytes); // 1 = positive signum
            int fallbackRange = partitions.length - FALLBACK_START;
            return FALLBACK_START + hashInt.mod(BigInteger.valueOf(fallbackRange)).intValue();
        } catch (Exception e) {
            System.out.println("Exception when trying to partition symbol " + symbol + ": " + e);
            return partitions[0];
        }
    }
}