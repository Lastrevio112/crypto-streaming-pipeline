"""Function that both producers will use to reconnect after 23 hours, in order to prevent disconnection."""

import threading
import time

def run_with_reconnect(producer, interval_hours=23):
    while True:
        t = threading.Thread(target=producer.run, daemon=True)
        t.start()
        time.sleep(interval_hours * 3600)
        producer.stop()  
        t.join(timeout=10)  # wait for clean shutdown before restarting
        producer.reset()  # recreate WebSocketApp before next iteration
        print(f"Reconnecting after {interval_hours}h...")