import websocket
from confluent_kafka import Producer
from abc import ABC, abstractmethod
import sys
import threading
import json

class WebSocketProducer(ABC):
    def __init__(self, url: str, streams: list, producer: Producer, topic: str):
        self.url = url
        self.streams = streams
        self.producer = producer
        self.topic = topic
        
        self.reset()

    def reset(self):
        self._stop_ping = threading.Event()
        self._ping_thread = None
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
    
    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection closed. Flushing Kafka producer.")
        self.producer.flush()

    @abstractmethod
    def on_message(self, ws, message):
        # Child classes will implement this method to verify whether we connected succesfully to the stream and produce to Kafka topics
        pass
    
    @abstractmethod
    def on_open(self, ws):
        # Child classes will implement this method to subscribe to the correct stream - this is data source specific
        pass

    def ping_pong(self, ping_json_message, ping_interval_seconds):
        if self._ping_thread is not None and self._ping_thread.is_alive():
            return  # do not call if it's already running
        
        self._stop_ping.clear()
    
        def ping_loop():
            while not self._stop_ping.wait(ping_interval_seconds):  # wait returns True if set, False on timeout
                try:
                    self.ws.send(ping_json_message)
                except Exception as e:
                    print(f"Ping failed: {e}")
                    break

        ping_thread = threading.Thread(target=ping_loop, daemon=True)
        ping_thread.start()
    
    def run(self):
        self.ws.run_forever(ping_interval=20, ping_timeout=10)

    # This method is needed in data source 2 to close the connection after 23h and restart it
    def stop(self):
        self._stop_ping.set()  # signal ping thread to exit     
        if self.ws:
            self.ws.close()
