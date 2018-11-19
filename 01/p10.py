# 关于self的案例

class A():
    name = " liuying"
    age = 18

    def __init__(self):
        self.name = "aaaa"
        self.age = 200

    def say(self):
        print(self.name)
        print(self.age)


class B():
    name = "bbbb"
    age = 90


#a = A()
# 此时，系统会默认把a作为第一个参数传入函数
#a.say()

# 此时，self被a替换
#A.say(a)
# 同样可以把A作为参数传入
#A.say(A)

# 此时，传入的是类实例B，因为B具有name和age属性，所以不会报错
A.say(B)

# 以上代码，利用了鸭子模型