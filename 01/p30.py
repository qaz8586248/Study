from optparse import OptionParser

def opt():
    parser = OptionParser("Usage: %prog -P -f -b -p")
    parser.add_option("-P", "--port",
                      dest="port",
                      action="store",
                      default="3306",
                      help='port 3306')
    parser.add_option("-f", "--tarfile",
                      dest="tarfile",
                      action="store",
                      default="/tmp/mysql-5.6.28-linux-glibc2.5-x86_64.tar.gz",
                      help='file  /tmp/mysql-5.6.28-linux-glibc2.5-x86_64.tar.gz')
    parser.add_option("-b", "--bashfile",
                      dest="myfile",
                      action="store",
                      default="/tmp/createmycnf.sh",
                      help='file  /tmp/createmycnf.sh')
    parser.add_option("-p", "--mysqlpwd",
                      dest="mysqlpwd",
                      action="store",
                      default="123456",
                      help='password 123456')
    options, args = parser.parse_args()
    return options, args

s,v=opt()
print(s,v)