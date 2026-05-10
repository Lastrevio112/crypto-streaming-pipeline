package com.crypto.udaf;

public class FirstValueAggFunction extends BoundaryValueAggFunction {

    @Override
    protected boolean isBetterTimestamp(long candidate, long current) {
        return candidate < current;
    }

    @Override
    protected long initialTimestamp() {
        return Long.MAX_VALUE;
    }
}