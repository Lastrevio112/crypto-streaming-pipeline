package com.crypto.udaf;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.table.functions.AggregateFunction;
import java.sql.Timestamp;


// A parent class that the children should inherit from. It defines merge and accumulate behavior, 
// while the child classes just define how we compare two rows.
public abstract class BoundaryValueAggFunction extends AggregateFunction<Double, BoundaryValueAggFunction.Accumulator> {
    // Accumulate defines what we are aggregating as values 'accumulate' in a sliding window. 
    // The 'value' variable is what the function will end up passing as a parameter in SQL.
    public static class Accumulator {
        public Double value = null;
        public long boundaryTimestamp;  
        public boolean hasValue = false;

        // Flink needs this default constructor for UDAFs:
        public Accumulator() {}

        // the constructor we actually use:
        public Accumulator(long initialTimestamp) {
            this.boundaryTimestamp = initialTimestamp;
        }
    }

    // Subclasses define whether "better" means earlier or later
    protected abstract boolean isBetterTimestamp(long candidate, long current);
    protected abstract long initialTimestamp();

    @Override
    public Accumulator createAccumulator() {
        return new Accumulator(initialTimestamp());
    }

    // java.sql.Timestamp is the compatible-equivalent of TIMESTAMP(3) in Flink SQL - Essentially this is what we're passing to the UDAF.
    public void accumulate(Accumulator acc, Double value, Timestamp timestamp) {
        if (value == null || timestamp == null) return;             //making this null-safe
        long timestamp_ms = timestamp.getTime();   // gives miliseconds since epoch
        if (isBetterTimestamp(timestamp_ms, acc.boundaryTimestamp)) {
            acc.value = value;
            acc.boundaryTimestamp = timestamp_ms;
            acc.hasValue = true;
        }
    }

    // Each time we encounter a new accumulator, we check whether its  value is smaller/larger (depending on child class) than the current value. 
    // Then we update the accumulated (that is, the current candidate for the return of the function) value with the current value.
    public void merge(Accumulator acc, Iterable<Accumulator> iterable) {
        for (Accumulator curr_row : iterable) {
            if (curr_row.hasValue && isBetterTimestamp(curr_row.boundaryTimestamp, acc.boundaryTimestamp)) {
                acc.value = curr_row.value;
                acc.boundaryTimestamp = curr_row.boundaryTimestamp;
                acc.hasValue = true;
            }
        }
    }

    public void retract(Accumulator acc, Double value, Timestamp timestamp) {
        acc.hasValue = false;
        acc.boundaryTimestamp = initialTimestamp();
        acc.value = null;
    }

    // Here we define what the function actually returns.
    @Override
    public Double getValue(Accumulator acc) {
        return acc.hasValue ? acc.value : null;
    }

    @Override
    public TypeInformation<Double> getResultType() {
        return TypeInformation.of(Double.class); //this is null safe compared to Types.DOUBLE, in case all prices within a window are NULL
    }

}