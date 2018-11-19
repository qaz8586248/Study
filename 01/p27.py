from optparse import OptionParser
optParser = OptionParser()
optParser.add_option('-f','--file',action = 'store',type = "string" ,dest = 'filename')
optParser.add_option("-v","--vison", action="store", dest="verbose",
                     default='hello',help="make lots of noise [default]")

fakeArgs = ['-f','file.txt','-v','how are you', 'arg1', 'arg2']
option , args = optParser.parse_args()
op , ar = optParser.parse_args(fakeArgs)
print("option : ",option)
print("args : ",args)
print("op : ",op)
print("ar : ",ar)
