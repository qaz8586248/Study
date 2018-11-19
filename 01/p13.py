# # 构造函数的调用顺序 - 3
class A():
    def __init__(self):
        print("A")


class B(A):
    def __init__(self, name):
        print("B")
        print(name)


class C(B):
    # c中想扩展B的构造函数，
    # 即调用B的构造函数后在添加一些功能
    # 由两种方法实现

    '''
    # 第一种是通过父类名调用
    def __init__(self, name):
        # 首先调用父类构造函数
        B.__init__(self, name)
        # 其次，再增加自己的功能
        print("这是C中附加的功能")
    '''

    # 第二种，使用super调用
    def __init__(self, name):
        # 首先调用父类构造函数
        super(C, self).__init__(name)
        # 其次，再增加自己的功能
        print("这是C中附加的功能{0}".format(name))


# 此时，首先查找C的构造函数
# 如果没有，则向上按照MRO顺序查找父类的构造函数，知道找到为止
# 此时，会出现参数结构不对应错误
c = C("我是C")