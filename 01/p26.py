import os

mydir=os.getcwd()
print(mydir)

ld=os.listdir()
print(ld)

absp = os.path.abspath("..")
print(absp)

bn=os.path.basename("C:/Users/jn/PycharmProjects/test03/01/p01.py")
print(bn)

e = os.path.exists("C:/Users/jn/PycharmProjects/test03/01/p01.py")
print(e)