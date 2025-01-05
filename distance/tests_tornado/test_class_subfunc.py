class A(list):
    def hello(self):
        def a():
            # 类内部并列函数能否看到彼此？可以
            print(f'b address is {b}')
            b()

        def b():
            #实例函数的子函数能否使用self？可以
            print(self.__len__())

        a()

A([_ for _ in range(4)]).hello()