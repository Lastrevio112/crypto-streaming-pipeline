""" We will split our topics into 10 partitions based on the hash of the cryptocurrency.
    Five most active coins will get their own partition, the other 45 coins will be distributed across the remaining five."""
import hashlib

def custom_partitioner(key: str, num_partitions: int):
    PARTITION_MAP = {
        "ETHUSDT": 0,
        "BTCUSDT": 1,
        "SUIUSDT": 2,
        "SOLUSDT": 3,
        "CHIPUSDT": 4
    }
    FALLBACK_START = 5 # Partitions 5-9 for the remaining coins

    if key in PARTITION_MAP:
        return PARTITION_MAP[key]
    
    # hash remaining keys into the leftover partition range
    hash_bytes = hashlib.md5(key.encode()).digest()
    hash_int = int.from_bytes(hash_bytes, 'big')
    fallback_range = num_partitions - FALLBACK_START
    
    return FALLBACK_START + (hash_int % fallback_range)