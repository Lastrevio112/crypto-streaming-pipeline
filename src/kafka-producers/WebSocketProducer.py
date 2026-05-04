import websocket
import json 
from confluent_kafka import Producer
from abc import ABC, abstractmethod

class WebSocketProducer(ABC):
    def __init__(self, url: str, streams: list, producer: Producer, topic: str):
        self.url = url
        self.streams = streams
        self.producer = producer
        self.topic = topic
        
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
    
    def run(self):
        self.ws.run_forever(ping_interval=20, ping_timeout=10)
