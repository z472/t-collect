# from test_amqp import runtornado,thread_data
from sample.tornadoconn.rabbitmqconn.rbmqclient import RbmqClient
from sample.tornadoconn.tornadoserver import main as startcoro_tornadoserver
import asyncio
import threading,time,sys,types
from queue import Queue

# 想跨线程让pika.TornadoConnection去ch.queue_declare，听说pika ch
# 和conn都不是线程安全的，这里确实是跨线程传conn了，但我通过支持线程安全
# queue.Queue()来保存对象了。并且也没有在别的线程里去ch.queue_declare
# （那是这代码最初版本），现在是通过Tornado主loop的add_callback去在ch
# 本地线程去执行。  实际debug的问题是，queue_declare前貌似都没有问题，
# 但该方法很神奇的是也没有问题，但在调用该方法的create_queue()完成后，
# 连接的ch状态自动设置为了closed，连接还在但ch消失。
# 可能会问在原来基础上直接创建不好吗？因为不想动之前测试好的代码，所以就
# 出现了这么激进的操作。碰壁后还是简单化吧。

'''
查/var/log/rabbitmq/rabbit@DESKTOP-K2DB76K.log 看到，终于有清晰的错误提示了
2024-12-25 21:54:39.393 [error] <0.6934.0> Channel error on connection 
<0.6926.0> (127.0.0.1:49678 -> 127.0.0.1:5672, vhost: 'fortest', user: 
'admin'), channel 1:operation queue.declare caused a channel exception 
access_refused: access to queue 'fwwrw' in vhost 'fortest' refused for
user 'admin'

指令秒了
sudo rabbitmqctl set_permissions -p "fortest" "admin" ".*" ".*" ".*"
'''
tl = Queue()

def runtornado(start_rabbitmq:bool=True):    
    async def inner_run(): 
        global tl         
        asyncio.get_running_loop()
        amqp_url = 'amqp://admin:admin@127.0.0.1:5672/fortest'
        rbclient = RbmqClient(amqp_url=amqp_url)
        if start_rabbitmq:
            tl.put((rbclient,rbclient.loop))
        await startcoro_tornadoserver()
    # the api whatever value of force_new_loop, event loop
    # run in the another thread. doc said it's asyncio.run
    # enhanced version but asyncio.run loop run current thread.
    #async_to_sync(inner_run, force_new_loop=True)()
    asyncio.run(inner_run())
            
def t_multithread_create_queues():
    def waitbackthread():
        while tl.empty():
            time.sleep(1)
        return tl.get()
     
    def currthread():        
        queue_names = ['test'+str(_) for _ in range(2)]
        rb, tioloop = waitbackthread()
        for name in queue_names:
            # this lazy load,so in fact when run first func
            # name var value is test1.Note!
            # tioloop.add_callback(lambda rb:rb.create_queue(name), rb)
            tioloop.add_callback(
                lambda rb,name:rb.create_queue(name), 
                *(rb,name))
               
    background = threading.Thread(target=runtornado,name='t_server')       
    back2 = threading.Thread(target=currthread,name='t_create_queue')
    background.start() 
    back2.start()
    background.join()
    back2.join()
    
if __name__ == '__main__':
    t_multithread_create_queues()
    
    
    