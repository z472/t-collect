from sample.tornadoconn.rabbitmqconn.rbmqclient import RbmqClient
from sample.tornadoconn.tornadoserver import main as startcoro_tornadoserver
import asyncio
import tornado,pika
from asgiref.sync import async_to_sync
import threading
from tornado.ioloop import IOLoop

#tornado views :create tornado user and rab_queue for him


thread_data = threading.local()

def runtornado(start_rabbitmq:bool=True):    
    async def inner_run():
        #asyncio.get_running_loop() 
        amqp_url = 'amqp://admin:admin@127.0.0.1:5672/fortest'
        rbclient = RbmqClient(amqp_url=amqp_url)    
        if start_rabbitmq:
            thread_data.rbclient = rbclient
        await startcoro_tornadoserver()        
    # the api whatever value of force_new_loop, event loop
    # run in the another thread. doc said it's asyncio.run
    # enhanced version but asyncio.run loop run current thread.
    #async_to_sync(inner_run, force_new_loop=True)()
    asyncio.run(inner_run())

if __name__ == '__main__':        
    runtornado()    