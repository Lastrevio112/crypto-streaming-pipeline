package com.crypto.udaf;

import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.common.typeinfo.Types;
import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.catalog.DataTypeFactory;
import org.apache.flink.table.functions.AggregateFunction;
import org.apache.flink.table.types.DataType;
import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.annotation.FunctionHint;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

import java.math.BigDecimal;


// A parent class that the children should inherit from. It defines merge and accumulate behavior, 
// while the child classes just define how we compare two rows.
@FunctionHint(
    accumulator = @DataTypeHint(value = "RAW", bridgedTo = Accumulator.class),
    input = {
        @DataTypeHint("DECIMAL(21, 8)"),
        @DataTypeHint("TIMESTAMP(3)")
    },
    output = @DataTypeHint("DECIMAL(21, 8)")
)
public abstract class BoundaryValueAggFunction extends AggregateFunction<BigDecimal, Accumulator> {
    // Subclasses define whether "better" means earlier or later
    protected abstract boolean isBetterTimestamp(long candidate, long current);
    protected abstract long initialTimestamp();

    @Override
    public Accumulator createAccumulator() {
        return new Accumulator(initialTimestamp());
    }

    // java.time.LocalDateTime is the compatible-equivalent of TIMESTAMP(3) in Flink SQL - Essentially this is what we're passing to the UDAF.
    public void accumulate(Accumulator acc, BigDecimal value, LocalDateTime timestamp) {
        if (value == null || timestamp == null) return;             //making this null-safe
        long timestamp_ms = timestamp.toInstant(ZoneOffset.UTC).toEpochMilli();   // gives miliseconds since epoch
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

    public void retract(Accumulator acc, BigDecimal value, LocalDateTime timestamp) {
        acc.hasValue = false;
        acc.boundaryTimestamp = initialTimestamp();
        acc.value = null;
    }

    // Here we define what the function actually returns.
    @Override
    public BigDecimal getValue(Accumulator acc) {
        return acc.hasValue ? acc.value : null;
    }

}