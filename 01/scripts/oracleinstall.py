#!/usr/bin/env python3

import os
import sys
from optparse import OptionParser
from subprocess import Popen,PIPE
import shlex
import time
import re
import shutil
import tarfile
import stat
import logging
import pwd
import zipfile


logger = None
Oracle_Base_Dir = '/oracle/app/oracle/'
Oracle_Home_Dir = Oracle_Base_Dir + 'product/12.2.0/db_1'
Oracle_UNQNAME = 'itpuxdb'
Oracle_SID = 'itpux33'



def installpackage():
    exit_code = os.system('ping -c 5 www.baidu.com')
    if exit_code:
        logger.error("请检查网路连通性！")
        sys.exit(1)
    else:
        os.system("yum install -y autoconf automake binutils binutils-devel bison cpp dos2unix ftp gcc gcc-c++ lrzsz python-devel compat-db* compat-gcc-34 compat-gcc-34-c++ compat-libcap1 compat-libstdc++-33 compat-libstdc++-33.i686 glibc-* glibc-*.i686 libXpm-*.i686 libXp.so.6 libXt.so.6 libXtst.so.6 libXext libXext.i686 libXtst libXtst.i686 libX11 libX11.i686 libXau libXau.i686 libxcb libxcb.i686 libXi libXi.i686 libgcc_s.so.1 libstdc++.i686 libstdc++-devel libstdc++-devel.i686 libaio libaio.i686 libaio-devel libaio-devel.i686 ksh libXp libaio-devel numactl numactl-devel make -y sysstat -y unixODBC unixODBC-devel elfutils-libelf-devel-0.97 elfutils-libelf-devel redhat-lsb-core unzip")

def install_log():
        global logger
        fmt = '%(lineno)s %(asctime)s  [%(process)d]: %(levelname)s  %(filename)s  %(message)s'
        log_file = 'install.log'
        logger = logging.getLogger('mysqllogging')
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)

def setenv():
    list = []
    with open(r'/etc/passwd', 'r') as fd:
        for line in fd:
            matchoracle = re.search(r'oracle', line, re.I)
    with open(r'/etc/group', 'r') as fg:
        for line in fg:
            matchdba = re.search(r'dba', line, re.I)
            matchoinstall = re.search(r'oinstall', line, re.I)
            matchoper = re.search(r'oper', line, re.I)

    if not matchdba:
        os.system("/usr/sbin/groupadd -g 60002 dba")
    else:
        logger.info("组dba已经存在")

    if not matchoper:
        os.system("/usr/sbin/groupadd -g 60003 oper")
    else:
        logger.info("组oper已经存在")

    if not matchoinstall:
        os.system("/usr/sbin/groupadd -g 60001 oinstall")
    else:
        logger.info("组oper已经存在")

    if not matchoracle:
        os.system("useradd -u 61001 -g oinstall -G dba,oper oracle")
        os.system("echo 'oracle' | passwd --stdin 'oracle'")
    else:
        logger.info("oracle用户已经存在")

    with open(r'/home/oracle/.bash_profile', 'a') as fd:
        fd.write("export TMP=/tmp" + '\n')
        fd.write("export LANG=en_US" + '\n')
        fd.write("export TMPDIR=$TMP" + '\n')
        fd.write("export ORACLE_UNQNAME=itpuxdb" + '\n')
        fd.write("ORACLE_SID=itpuxdb; export ORACLE_SID" + '\n')
        fd.write("ORACLE_BASE=/oracle/app/oracle; export ORACLE_BASE" + '\n')
        fd.write("ORACLE_HOME=$ORACLE_BASE/product/12.2.0/db_1; export ORACLE_HOME" + '\n')
        fd.write("ORACLE_TERM=xterm; export ORACLE_TERM" + '\n')
        fd.write('NLS_DATE_FORMAT="yyyy-mm-dd HH24:MI:SS"; export NLS_DATE_FORMAT' + '\n')
        fd.write("NLS_LANG=AMERICAN_AMERICA.ZHS16GBK;export NLS_LANG" + '\n')
        fd.write("PATH=.:$PATH:$HOME/.local/bin:$HOME/bin:$ORACLE_HOME/bin; export PATH" + '\n')
        fd.write("THREADS_FLAG=native; export THREADS_FLAG" + '\n' + "umask=022" + '\n')
        fd.write('if [ $USER = "oracle" ]; then' + '\n' + 'if [ $SHELL = "/bin/ksh" ]; then' + '\n')
        fd.write('ulimit -p 16384' + '\n' + 'ulimit -n 65536' + '\n')
        fd.write('else' + '\n' + 'ulimit -u 16384 -n 65536' + '\n')
        fd.write('fi' + '\n' + 'umask 022' + '\n' + 'fi' + '\n')
    os.system('source /home/oracle/.bash_profile')

def opt():
    parser = OptionParser("Usage: %prog  -f ")
#    parser.add_option("-P", "--port", dest="port", action="store", default="3306", help="port 3306")
    parser.add_option("-f", "--tarfile", dest="tarfile", action="store", default="/soft/linuxx64_12201_database.zip", help="file location")
#    parser.add_option("-p", "--mysqlpwd", dest="mysqlpwd", action="store", default="123456", help="pwd 123456")
    options,args = parser.parse_args()
    return options,args

def make_dir():
    if os.path.exists(Oracle_Base_Dir):
        logger.error("Oracle is already install")
        sys.exit(1)
    try:
        os.makedirs(Oracle_Base_Dir + 'product/12.2.0/db_1')
        os.makedirs('/oradata')
        os.makedirs('/oracle/app/oraInventory/')
    except Exception as e:
        logger.error(e)

def extract(oraclefile):
    if not os.path.exists(oraclefile):
        logger.error("{0} is not exists".format(oraclefile))
        sys.exit(1)
    os.system("chown -R oracle:oinstall /soft")
    os.system("su - oracle -c 'unzip {0} -d /soft'".format(oraclefile))

def setowner():
    list = []
    os.system("chown -R oracle:oinstall /oracle")
    os.system("chown -R oracle:oinstall /oradata")
    os.system("chmod -R 775 /oracle")
    os.system("chmod -R 775 /oradata")

    for i in pwd.getpwnam('oracle'):
        list.append(i)
    oracleuid = list[2]
    oraclgid = list[3]
    stdatadirmode = os.stat(Oracle_Base_Dir).st_mode
    stappdirmode = os.stat(Oracle_Home_Dir).st_mode
    if not (os.stat(Oracle_Base_Dir).st_uid == oracleuid and os.stat(Oracle_Base_Dir).st_gid ==oraclgid):
        logger.error("chown oracle basedir or installdir not ok")
        sys.exit(1)
    if not (os.stat(Oracle_Home_Dir).st_uid == oracleuid and os.stat(Oracle_Home_Dir).st_gid == oraclgid):
        logger.error("chown oracle homedir or installdir not ok")
        sys.exit(1)

def oracleinstall():
    if not os.path.exists('/soft/db_install.rsp'):
        logger.error("Install document db_install.rsp do not exist,please upload to /soft")
        sys.exit(1)
    else:
        os.system("su - oracle -c 'cp -r /soft/database/response /oracle/'")
        os.system("su - oracle -c 'mv /oracle/response/db_install.rsp /oracle/response/db_install.rsp.bak'")
        os.system("su - oracle -c 'cp /soft/db_install.rsp /oracle/response/'")
        os.system("su - oracle -c 'chmod 775 /oracle/response/db_install.rsp '")
        with open(r'/etc/oraInst.loc', 'w') as fg:
            fg.writelines("inventory=/oracle/app/oraInventory")
            fg.writelines("inst_group=oinstall")
        os.system("chown oracle:oinstall /etc/oraInst.loc")
        os.system("su - oracle -c '/soft/database/runInstaller -silent -force -noconfig -responseFile /oracle/response/db_install.rsp'")

def listenerinstall():
    if not os.path.exists('/soft/netca.rsp'):
        logger.error("Install document netca.rsp do not exist,please upload to /soft")
        sys.exit(1)
    else:
        os.system("su - oracle -c 'mv /oracle/response/netca.rsp /oracle/response/netca.rsp.bak'")
        os.system("su - oracle -c 'cp /soft/netca.rsp /oracle/response/'")
        os.system("su - oracle -c 'chmod 775 /oracle/response/netca.rsp'")
        os.system("su - oracle -c 'netca -silent -responsefile /oracle/response/netca.rsp'")

def dbcreate():
#    os.system("su - oracle -c 'mv /oracle/response/dbca.rsp /oracle/response/dbca.rsp.bak'")
#    os.system("su - oracle -c 'cp /soft/dbca.rsp /oracle/response/'")
#    os.system("su - oracle -c 'chmod 775 /oracle/response/dbca.rsp'")
    os.system("su - oracle -c 'dbca -silent -createDatabase -templateName General_Purpose.dbc -gdbName itpuxdb -sid itpuxdb -databaseConfigType SI -responseFile NO_VALUE -sysPassword oracle -systemPassword oracle -characterSet ZHS16GBK -memoryPercentage 30 -emConfiguration LOCAL'")

def checkinstall(port):
    if not os.path.exists('/mysql/data/{0}/data/ibdata1'.format(port)):
        logger.error('mysql not install ')
        sys.exit(1)
    with open(r'/mysql/log/{0}/itpuxdb-error.err'.format(port), 'r') as fd:
        fdlist = [i for i in fd if i]
        fdstr = ''.join(fdlist)
        re_error = re.compile(r'\s\[error\]\s', re.M | re.I)
        errorlist = re_error.findall(fdstr)
    if errorlist:
        logger.error('error.log error count:' + str(len(errorlist)))
        logger.error('mysql not install ')
        sys.exit(1)
    else:
        logger.info('install mysql  ok')




if __name__ == '__main__':
    install_log()
    options,args = opt()
    try:
        cmd = args[0]
    except IndexError:
        print("%s follow a command" % __file__)
        print("%s -h" % __file__)
        sys.exit(1)

    if (options.tarfile and os.path.isfile(options.tarfile)):
        oraclefile = options.tarfile
    else:
        print("%s -h" % __file__)
        sys.exit(1)
    if cmd == 'create':
        installpackage()
        logger.info('step1:installpackage completed')

        setenv()
        logger.info('step2:setenv completed')

        make_dir()
        logger.info('step3:makeDIR completed')

        extract(oraclefile)
        logger.info('step4:extract completed')

        setowner()
        logger.info('step5:setOwner completed')

        oracleinstall()
        logger.info('step6:oracleinstall completed')

        p = input("请另开一个窗口，使用root执行相关脚本，执行成功后，请按yes继续：")
        while True:
            if p in ['yes','Yes','YES']:
                listenerinstall()
                logger.info('step7:listenerinstall completed')
                break
            else:
                p = input("请另开一个窗口，使用root执行相关脚本，执行成功后，请按yes继续：")

        dbcreate()
        logger.info("请使用root用户执行相关脚本")
        logger.info('step9:dbcreate completed')

        print('oracle install finish')