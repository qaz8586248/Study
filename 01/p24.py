import time

print(time.daylight)
print(time.timezone)
print(time.altzone)
time.time()

t = time.localtime()
print(t)

tt = time.asctime(t)
print(type(tt))
print(tt)

t = time.ctime()
print(type(t))
print(t)

print(time.mktime(time.strptime("2018-11-19","%Y-%m-%d")))

current_st = time.time()
print(current_st)

t = time.localtime()
ft = time.strftime("%Y-%m-%d" , t)

print(ft)

print(type(time.strptime("2018-11-19","%Y-%m-%d")))
print(type(time.strftime("%Y-%m-%d",time.localtime())))