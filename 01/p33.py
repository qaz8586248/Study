import _pickle as cPickle


alist = ['who','am','I']
blist = ['god','know''?']
filename = 'test.data'
f = file(filename, 'a')
p.dump(alist,f)
p.dump(blist

 f = file('test01.txt')
 while True:
     try:
        print p.load(f)
     except EOFError:
        break