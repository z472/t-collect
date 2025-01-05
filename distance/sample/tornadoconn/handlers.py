import tornado
import threading 

handlers_local = threading.local()
handlers_local.connsum = 0

class MainPageHandler(tornado.web.RequestHandler):
    
    def initialize(self, userid:int):
        print('Userid:',int(userid))
        handlers_local.connsum += 1
        
    def get(self, anystr:str):
        print(f'From {anystr} {handlers_local.connsum} requests.')