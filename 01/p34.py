# 使用shelve创建文件并使用
import shelve

shv = shelve.open(r'shv.db')

shv['one'] = 1
shv['two'] = 2
shv['three'] = 3

shv.close()



# shelve读取案例
shv = shelve.open(r'shv.db')

try:
    print(shv['one'])
    print(shv['three'])
except Exception as e:
    print("烦死了")
finally:
    shv.close()