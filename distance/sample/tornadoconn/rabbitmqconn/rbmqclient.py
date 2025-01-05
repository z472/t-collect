from abc import ABC, abstractmethod
import logging
import pika
from pika import adapters
from pika.spec import Basic
from pika.adapters.tornado_connection import TornadoConnection
from pika.exchange_type import ExchangeType
from collections import defaultdict
from typing import Callable, Any, Mapping
from pika.channel import Channel
import orjson,threading
from pika.adapters.select_connection import SelectConnection
import asyncio

LOGGER = logging.getLogger(__name__)

# control the rpc calls between tornado and rabbitmq by Pika.
# refer to https://pika.readthedocs.io/en/stable/examples/tornado_consumer.html
# https://pika.readthedocs.io/en/stable/intro.html
class RbmqClient():
    def __init__(self, amqp_url) -> None:      
        self.log = logging.getLogger("distance.queue")  
        self._url = amqp_url
        self.loop = None
        self._channel = None             
        # record queues's name in rabbitmq broker
        self.queues = set()
        
        self._connection = self._connect()
                
    def _connect(self):
        try:            
            conn = TornadoConnection(
                pika.URLParameters(self._url),                                 
                on_open_callback=self.on_connection_open)
            self.loop = conn.ioloop
        finally:
            return conn
        
    def on_connection_open(self, unused_connection):
        assert self._connection is not None 
        self._connection.channel(on_open_callback=self.on_channel_open)
        
    def on_channel_open(self, channel:Channel):
        assert channel is not None
        self._channel = channel
               
    def create_queue(self, queue_name:str)->None:
        def set_qos(frame: Any) -> None:
            assert self._channel is not None
            self.queues.add(queue_name)
                              
        if queue_name in self.queues:
            # "RabbitMQ does not allow you to redefine an existing 
            # queue with different parameters"
            # call create_queue() func should catch Error.
            print('create twice.')
            raise RuntimeError
        self._channel.queue_declare(
            queue=queue_name,
            #this var ad doc said when disconnects, then
            auto_delete=True,
            durable=True, 
            callback=set_qos)
        print(f'create a new queue {queue_name}.')  
                
    def control_queue(self, queue_name:str, callback:Callable[[Channel],None]=None)->None:        
        if self._channel is None:
            return 
        if queue_name not in self.queues:
            raise KeyError(f'No {queue_name} to control queue.')        
        callback(self._channel)
            
    
    def publish(self, queue_name: str, body: Mapping[str, Any]) -> None:
        def do_publish(channel: Channel) -> None:
            body = orjson.dumps(body)
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                # 2 = durable, 1 = transient
                properties=pika.BasicProperties(delivery_mode=2),
                body=body,
            )

        self.control_queue(queue_name, do_publish)
    
    def create_queue_consumer(self, queue_name:str, 
            workerfunc:Callable[[list[Mapping[str,Any]]],None]
        ) -> None:
        def wrapped_consumer(
                ch: Channel,
                method: Basic.Deliver,
                properties: pika.BasicProperties,
                body: bytes,
            ) -> None:
                assert method.delivery_tag is not None        
                workerfunc([orjson.loads(body)])
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
        def do_consume(channel:Channel):            
            channel.basic_consume(
                queue_name,
                on_message_callback=wrapped_consumer,
                consumer_tag=self._generate_ctag(queue_name),
            )
        self.control_queue(queue_name, do_consume)
        
thread_data = threading.local()

def get_rbmqclient()->RbmqClient:
    if not hasattr(thread_data, "rbmqclient"):
        raise RuntimeError('No Rbmqclient in current thread')
    return thread_data.rbmqclient

def set_queue_client(rbmqclient: RbmqClient) -> None:
    thread_data.rbmqclient = rbmqclient