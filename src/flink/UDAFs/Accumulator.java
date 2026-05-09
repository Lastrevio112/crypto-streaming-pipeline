package com.crypto.udaf;

import java.math.BigDecimal;

// Accumulate defines what we are aggregating as values 'accumulate' in a sliding window. 
// The 'value' variable is what the function will end up passing as a parameter in SQL.
public class Accumulator {
    public BigDecimal value = null;
    public long boundaryTimestamp;
    public boolean hasValue = false;

    public Accumulator() {}

    public Accumulator(long initialTimestamp) {
        this.boundaryTimestamp = initialTimestamp;
    }
}