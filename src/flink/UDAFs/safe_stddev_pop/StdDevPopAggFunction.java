// Yes, I am implementing my own UDAF even though Flink SQL already has a STDDEV_POP method.
// This is because Flink's method has a bug that converts values to DECIMAL(38,8) as an intermediary step in the calculations.
// This fucks up my entire pipeline and leads to an error like: "java.lang.NumberFormatException: Character N is neither a decimal digit number, decimal point, nor "e" notation exponential mark."

package com.crypto.udaf;

import org.apache.flink.table.functions.AggregateFunction;
import org.apache.flink.table.types.DataType;
import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.annotation.FunctionHint;

import java.math.BigDecimal;

@FunctionHint(
    accumulator = @DataTypeHint(value = "RAW", bridgedTo = StdDevAccumulator.class),
    input = { @DataTypeHint("DECIMAL(21, 8)") },    // I am only using it for this type of input, I know it's not generic but it's a "use-once" thing
    output = @DataTypeHint("DOUBLE")
)
public class StdDevPopAggFunction extends AggregateFunction<Double, StdDevAccumulator> {

    @Override
    public StdDevAccumulator createAccumulator() {
        return new StdDevAccumulator();
    }

    public void accumulate(StdDevAccumulator acc, BigDecimal value) {
        if (value == null) return;
        double v = value.doubleValue();
        acc.sum += v;
        acc.sumOfSquares += v * v;
        acc.count++;
    }

    public void merge(StdDevAccumulator acc, Iterable<StdDevAccumulator> it) {
        for (StdDevAccumulator curr : it) {
            acc.sum += curr.sum;
            acc.sumOfSquares += curr.sumOfSquares;
            acc.count += curr.count;
        }
    }

    public void retract(StdDevAccumulator acc, BigDecimal value) {
        if (value == null || acc.count == 0) return;
        double v = value.doubleValue();
        acc.sum -= v;
        acc.sumOfSquares -= v * v;
        acc.count--;
    }

    @Override
    public Double getValue(StdDevAccumulator acc) {
        if (acc.count == 0) 
            return null;
        else if (acc.count == 1)
            return 0.0;
            
        double variance = (acc.sumOfSquares - (acc.sum * acc.sum) / acc.count) / acc.count;
        return Math.sqrt(Math.max(variance, 0.0));  // clamp float noise
    }
}