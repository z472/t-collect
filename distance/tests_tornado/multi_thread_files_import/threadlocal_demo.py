import threading

threadLocal = threading.local()

def print_message():
   name = getattr(threadLocal, 'name', None);
   print(name)
   return

class Executor(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        # Store name in object using self reference
        self.name = name

    def run(self):
        # Here we copy from object to local context,
        # since the thread is running
        threadLocal.name = self.name
        print_message()

A = Executor("A")
A.start()
B = Executor("B")
B.start()
print(vars(threadLocal))