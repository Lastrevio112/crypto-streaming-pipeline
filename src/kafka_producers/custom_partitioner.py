""" We will split our topics into 10 partitions based on the hash of the cryptocurrency.
    Five most active coins will get their own partition, the other 45 coins will be distributed across the remaining five."""

def custom_partitioner(key: str, num_partitions: int):
    PARTITION_MAP = {
        "BABYUSDT": 0,
        "ETHUSDT": 1,
        "MEGAUSDT": 2,
        "CHIPUSDT": 3,
        "BTCUSDT": 4
    }
    FALLBACK_START = 5 # Partitions 5-9 for the remaining coins

    if key in PARTITION_MAP:
        return PARTITION_MAP[key]
    
    # hash remaining keys into the leftover partition range
    fallback_range = num_partitions - FALLBACK_START
    return FALLBACK_START + (hash(key) % fallback_range)