import re

with open('test', 'r') as fd:
    fdlist = [i for i in fd]
    fdstr="".join(fdlist)
    print(fdstr)
    re_error=re.compile(r'error',re.I | re.M)
    errorlist=re_error.findall(fdstr)
    print(len(errorlist))

    print("%s follow a command" % __file__)