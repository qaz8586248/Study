# 收集参数的解包问题

def stu(*args):
    print("哈哈哈哈哈")
    # n 用来表示循环次数
    # 主要用来调试
    n = 0
    for i in args:
        print(type(i))
        print(n)
        n += 1
        print(i)


# stu("liuying", "liuxiaoyhing", 19, 200)

l = ["liuying", 19, 23, "wangxiaojing"]

# stu(l)
# 此时，args的表示形式是字典内一个list类型的元素，即 arg = (["liuying", 19, 23, "wangxiaojing"],)
# 很显然跟我们最初的想法违背


# 此时的调用，我们就需要解包符号，即调用的时候前面加一个星号
stu(*l)