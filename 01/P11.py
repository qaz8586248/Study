# 私有变量案例

class Person():
    # name是共有的成员
    name = "liuying"
    # __age就是私有成员
    __age = 18


p = Person()
# name是公有变量
print(p.name)
# __age是私有变量
print(p._Person__age)