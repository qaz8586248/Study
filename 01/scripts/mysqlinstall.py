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
import pymysql

logger = None
Mysql_Data_Dir = '/mysql/data/'
Mysql_Log_Dir = '/mysql/log/'
Mysql_App_Dir = '/mysql/app/mysql/'
Mysql_Conf_dir = ''
Mysql_Start_Dir = '/etc/init.d/'
Init_Conf = '/soft/my.cnf'

def rm_mysql():
    list = []
    cmd = "rpm -qa|grep mariadb"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    if stdout:
        list = stdout.decode().split()
    if stderr:
        print("error")
    for i in list:
        if "libs" not in i:
            os.system("rpm -e {0} --nodeps".format(i))
def install_log():
        global logger
        fmt = '%(lineno)s %(asctime)s  [%(process)d]: %(levelname)s  %(filename)s  %(message)s'
        log_file = 'install.log'
        logger = logging.getLogger('mysqllogging')
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)

def opt():
    parser = OptionParser("Usage: %prog -P -f -p")
    parser.add_option("-P", "--port", dest="port", action="store", default="3306", help="port 3306")
    parser.add_option("-f", "--tarfile", dest="tarfile", action="store", default="/soft/mysql-5.7.20-linux-glibc2.12-x86_64.tar.gz", help="file location")
    parser.add_option("-p", "--mysqlpwd", dest="mysqlpwd", action="store", default="123456", help="pwd 123456")
    options,args = parser.parse_args()
    return options,args

def make_dir(port):
    global  Mysql_Conf_dir
    if os.path.exists('/mysql/data/{0}/data'.format(port)):
        logger.error("mysql {0} is already install".format(port))
        sys.exit(1)
    try:
        os.makedirs('/mysql/data/{0}/data/'.format(port))
        os.makedirs('/mysql/log/{0}/'.format(port))
        Mysql_Conf_dir = '/mysql/data/{0}/'.format(port)
        os.system('touch /mysql/log/{0}/itpuxdb-error.err'.format(port))
    except Exception as e:
        logger.error(e)

def extract(mysqlfile):
    if not os.path.exists(mysqlfile):
        logger.error("{0} is not exists".format(mysqlfile))
        os._exit(1)
    os.chdir(os.path.dirname(mysqlfile))
    t = tarfile.open(mysqlfile, 'r:gz')
    t.extractall()
    t.close()

def copyfile(mysqlfile):
    shutil.copytree(mysqlfile.split('.tar.gz')[0], Mysql_App_Dir)
    shutil.rmtree(mysqlfile.split('.tar.gz')[0])

def setowner(port):
    list = []
    with open(r'/etc/passwd', 'r') as fd:
        for line in fd:
            matchmysql = re.search(r'mysql', line, re.I)

    if matchmysql:
        os.system('chown -R mysql:mysql /mysql')
    else:
        os.system("useradd -M -s /sbin/nologin mysql")
        os.system("'chown -R mysql:mysql /mysql")

    for i in pwd.getpwnam('mysql'):
        list.append(i)
    mysqluid = list[2]
    mysqlgid = list[3]
    stdatadirmode = os.stat(Mysql_Data_Dir).st_mode
    stappdirmode = os.stat(Mysql_App_Dir).st_mode
    if not (os.stat(Mysql_Data_Dir).st_uid == mysqluid and os.stat(Mysql_App_Dir).st_gid ==mysqlgid):
        logger.error("chown mysql datadir or installdir not ok")
        sys.exit(1)
    if not (os.stat(Mysql_Data_Dir + '{0}/data'.format(port)).st_uid == mysqluid and os.stat(Mysql_Data_Dir + '{0}/data'.format(port)).st_gid ==mysqlgid):
        logger.error("chown mysql datadir or installdir not ok")
        sys.exit(1)
    if not (os.stat(Mysql_Log_Dir + '{0}'.format(port)).st_uid == mysqluid and os.stat(Mysql_Log_Dir + '{0}'.format(port)).st_gid == mysqlgid):
        logger.error("chown mysql datadir or installdir not ok")
        sys.exit(1)

def mysqlinstall(port):
    if not os.path.exists(Init_Conf):
        logger.error("Init mysql conf do not exist,please upload to /soft")
        sys.exit(1)
    else:
        shutil.copy2(Init_Conf,Mysql_Conf_dir)
        cmd = Mysql_App_Dir + "bin/mysqld --defaults-file={0}my.cnf --initialize --user=mysql --basedir={1} --datadir={2}{3}/data/".format(Mysql_Conf_dir,Mysql_App_Dir,Mysql_Data_Dir,port)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        stdout,stderr = p.communicate()
        if stdout:
            logger.info("install output: {0}".format(stdout))
        if stderr:
            logger.error("install error output: {0}".format(stderr))

        if p.returncode ==0:
            logger.info("initialize completed")
            logger.info("install returncode : {0}".format(p.returncode))
        else:
            logger.info('initialize failed , please check the mysql errror log')
            logger.info('install returncode: %s' % (p.returncode))
            sys.exit(1)

def setenv():
    with open(r'/etc/profile', 'a') as fd:
        fd.write("export PATH=$PATH:/mysql/app/mysql/bin" + '\n')
    os.system('source /etc/profile')

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

def mysqlstart():
    cmd = Mysql_App_Dir + "bin/mysqld --defaults-file=" + Mysql_Conf_dir + "my.cnf &"
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = p.communicate()
    if stdout:
        logger.info('mysql startup output: %s' % (stdout))
    if stderr:
        logger.error('mysql startup error output: %s' % (stderr))

    if p.returncode == 0:
        logger.info('mysql startup completed')
        logger.info('mysql startup returncode: %s' % (p.returncode))
    else:
        logger.info('mysql startup failed , please check the mysql errror log')
        logger.info('mysql startup returncode: %s' % (p.returncode))
        sys.exit(1)
    time.sleep(4)  # 休眠4秒 让mysql完全启动完毕

#def connmysql(port):
#    list1 = ""
#    list2 = []
#    with open(r'/mysql/log/{0}/itpuxdb-error.err'.format(port), 'r') as fg:
#        for i in fg:
#            if 'root@localhost' in i:
#                list1 = i
#    list2 = list1.split()
#    passwd = list2[-1]
#    host = 'localhost'
#    user = 'root'
#    dbname = 'mysql'
#    try:
#        db = pymysql.connect(host=host, user=user, passwd=passwd, db=dbname, port=port)
#    except Exception as e:
#        logger.error(e)
#        sys.exit(1)
#    cur = db.cursor()
#    return cur

def runsql(port,mysqlpwd):
    list1 = ""
    list2 = []
    with open(r'/mysql/log/{0}/itpuxdb-error.err'.format(port), 'r') as fg:
        for i in fg:
            if 'root@localhost' in i:
                list1 = i
    list2 = list1.split()
    passwd = list2[-1]
    os.system("mysqladmin -uroot -p'{0}' password '{1}' -S /mysql/data/{2}/mysql.sock".format(passwd,mysqlpwd,port))
#    sql = "alter user root@localhost identified  by '{0}'".format(mysqlpwd)
#    cur = connmysql(port)
#    cur.execute(sql)


if __name__ == '__main__':
    rm_mysql()
    install_log()
    options,args = opt()
    try:
        cmd = args[0]
    except IndexError:
        print("%s follow a command" % __file__)
        print("%s -h" % __file__)
        sys.exit(1)

    if (options.port and str.isdigit(options.port)) and (options.tarfile and os.path.isfile(options.tarfile)) and (options.mysqlpwd):
        mysqlport = options.port
        mysqlfile = options.tarfile
        mysqlpwd = options.mysqlpwd
    else:
        print("%s -h" % __file__)
        sys.exit(1)
    if cmd == 'create':

        make_dir(mysqlport)
        logger.info('step2:makeDIR completed')

        extract(mysqlfile)
        logger.info('step3:extract completed')

        copyfile(mysqlfile)
        logger.info('step4:copyFile completed')

        setowner(mysqlport)
        logger.info('step5:setOwner completed')

        mysqlinstall(mysqlport)
        logger.info('step6:mysql_install completed')

        setenv()
        logger.info('step7:setEnv completed')

        checkinstall(mysqlport)
        logger.info('step9:checkInstall completed')

        mysqlstart()
        logger.info('step10:mysqlserviceStart completed')

        runsql(mysqlport, mysqlpwd)
        logger.info('step11:runSQL completed')

        print('mysql install finish')



