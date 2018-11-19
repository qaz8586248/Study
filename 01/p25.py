import datetime
import time
import timeit

dt=datetime.datetime
print(dt.today())
print(dt.now())


def p():
    time.sleep(3.6)


t1 = time.time()
p()
print(time.time() - t1)


# timeit 可以执行一个函数，来测量一个函数的执行时间
def doIt():
    num = 3
    for i in range(num):
        print("Repeat for {0}".format(i))


# 执行函数，重复10次
t = timeit.timeit(stmt=doIt, number=10)
print(t)