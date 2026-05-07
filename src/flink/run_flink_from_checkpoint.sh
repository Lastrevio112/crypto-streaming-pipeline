#!/bin/bash

# Find the most recently written valid checkpoint by locating _metadata files,
# which Flink writes only after a checkpoint completes successfully.
# We take the deepest/latest one by sorting and picking the last result.
LATEST_META=$(find /opt/flink/checkpoints -name "_metadata" | sort | tail -1)

if [ -z "$LATEST_META" ]; then
  echo "No checkpoint found. Starting job from scratch."
  # If no checkpoint exists,  start the job with no state restoration.
  flink run -py /workspace/src/flink/execute_all_sql_files.py \
    -D rest.address=jobmanager -D rest.port=8081
else
  CHECKPOINT_DIR=$(dirname "$LATEST_META")
  echo "Resuming from checkpoint: $CHECKPOINT_DIR"
  # -s tells Flink to resume from that checkpoint path.
  # -n (--allowNonRestoredState) tells Flink to silently drop any state that can't be mapped to the current job graph, rather than failing hard on an incompatible checkpoint.
  flink run -py /workspace/src/flink/execute_all_sql_files.py \
    -D rest.address=jobmanager -D rest.port=8081 \
    -s "file://$CHECKPOINT_DIR" \
    -n
fi