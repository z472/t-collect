import asyncio,tornado
from .views import UserForTest


async def main():
    from .handlers import MainPageHandler
    default_user = UserForTest(id=0,name='John0',age=42)
    # URL regex -> handler's http method. dict -> their initialize()
    application = tornado.web.Application([
        (r"/user/(.*)", MainPageHandler, dict(userid=default_user.id)),
    ])
    server = tornado.httpserver.HTTPServer(application, xheaders=True)
    addr = "127.0.0.1"
    server.listen(8888)
    # 服务器非阻塞是针对多个请求IO上；你觉得服务器在ioLoop里阻塞，可能
    # 下面的代码event一直不被set()导致的，wait会阻塞，除非外部有人设置
    # event.set()。官网asyncio部分有例子，但这段又是tornado server固定
    # 写法，故tornado server对于所在的ioloop线程可以说是阻塞的。
    # 阻塞等同于不归还程序控制权
    await asyncio.Event().wait()
    
if __name__ == '__main__':
    asyncio.run(main())