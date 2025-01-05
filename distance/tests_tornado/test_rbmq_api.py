from sample.tornadoconn.rabbitmqconn.rbmqclient import RbmqClient
from sample.tornadoconn.tornadoserver import main as startcoro_tornadoserver
import asyncio,functools

def runtornado(start_rabbitmq:bool=True):    
    async def inner_run(): 
        async def cq(rb):
            while rb._channel == None:
                await asyncio.sleep(1)
            rb.create_queue('fwwrw')        
        amqp_url = 'amqp://admin:admin@127.0.0.1:5672/fortest'
        rbclient = RbmqClient(amqp_url=amqp_url)
        ioloop = rbclient.loop
        # the func will run before pika.channel create but
        # it should run after so this is async def.
        ioloop.add_callback(functools.partial(cq, rbclient))
        await startcoro_tornadoserver()
    
    asyncio.run(inner_run())

if __name__ == '__main__':
    runtornado()