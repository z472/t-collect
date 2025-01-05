from asgiref.sync import async_to_sync
import tornado,random
from test_amqp import runtornado
from time import time
from threading import currentThread,get_native_id
now = time()

def sfunc():
    def output(interval):
        print(f'timeout = {interval}!')
    ioloop = tornado.ioloop.IOLoop.current()
    print(f'sfunc thread id {get_native_id()}.')
    interval = 2 + random.randint(0, 10)
    ioloop.call_later(interval, output, interval)


def test_a_to_s(request_times):        
    for _ in range(request_times):
        sfunc()
        print(f'now is {time()-now}')

if __name__ == '__main__':
    runtornado(start_rabbitmq=False)
    print(f'Main thread id {get_native_id()}.')
    test_a_to_s(3)