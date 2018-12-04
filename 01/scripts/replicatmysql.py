#!/usr/bin/env python3

import os
import sys
from optparse import OptionParser
from subprocess import Popen, PIPE
import shlex
import time
import re
import shutil
import tarfile
import stat
import logging
import pwd
import paramiko
from functools import wraps
from datetime import datetime

logger = None
User = 'root'
Pwd = 'rootroot'
RelUser = 'repuser'
RelPwd = 'repuser123'
Mysql_Dir = '/mysql/'
Mysql_Data_Dir = '/mysql/data/'
Mysql_Log_Dir = '/mysql/log/'
Mysql_App_Dir = '/mysql/app/mysql/'
Mysql_Start_Dir = '/etc/init.d/'
Init_Conf = '/soft/my.cnf'
Start_Conf = '/soft/mysql.server'
Rm_Mysql = '/soft/rmmysql.py'


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(func.__name__, end - start)
        return result

    return wrapper()


class SSHManager():
    def __init__(self, host, usr, passwd):
        self._host = host
        self._usr = usr
        self._passwd = passwd
        self._ssh = None
        self._sftp = None
        self._ssh_connect()
        self._sftp_connect()

    def __del__(self):
        if self._ssh:
            self._ssh.close()
        if self._sftp:
            self._sftp.close()

    def _sftp_connect(self):
        try:
            transport = paramiko.Transport((self._host, 22))
            transport.connect(username=self._usr, password=self._passwd)
            self._sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            raise RuntimeError("sftp connect failed {0}".format(str(e)))

    def _ssh_connect(self):
        try:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(hostname=self._host, port=22, username=self._usr, password=self._passwd, timeout=5, allow_agent=False, look_for_keys=False)
        except Exception:
            raise RuntimeError(
                "ssh connect to [host:{0}, usr:{1}, passwd:{2} faile]".format(self._host, self._usr, self._passwd))

    def _exec_commnad(self, cmd):
        try:
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            logger.info("shanchu le me ")
            return stdout.read().decode()
        except Exception as e:
            raise RuntimeError('Exec command [%s] failed' % str(cmd))

    def ssh_exec_cmd(self, cmd):
        try:
            result = self._exec_commnad(cmd)
            print(type(result))
            return result
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    @staticmethod
    def is_file_exit(file_name):
        try:
            with open(file_name, 'r'):
                return True
        except Exception as e:
            return False

    #    @timethis
    def _upload_file(self, local_file, remote_file):
        try:
            self._sftp.put(local_file, remote_file)
        except Exception as e:
            raise RuntimeError("upload failed [{0}]".format(str(e)))

    def _check_remote_file(self, local_file, remote_file):
        try:
            result = self._exec_commnad('find ' + remote_file)
            if len(result) == 0:
                self._upload_file(local_file, remote_file)
            else:
                lf_size = os.path.getsize(local_file)
                result = self._exec_commnad('du -b ' + remote_file)
                rf_size = int(result.split('\t')[0])
                if lf_size != rf_size:
                    self._upload_file(local_file, remote_file)
        except Exception as e:
            raise RuntimeError("check error [{0}]".format(str(e)))

    def ssh_exec_shell(self, local_file, remote_file):
        try:
            if not self.is_file_exit(local_file):
                raise RuntimeError("File {0} not exist".format(local_file))

            self._check_remote_file(local_file, remote_file)

            result = self._exec_commnad('/usr/local/python3/bin/python3 ' + remote_file)
            print('exec python result: ', result)
        except Exception as e:
            raise RuntimeError("ssh exec shell failed {0}".format(str(e)))


def rm_mysql(ip):
    if not os.path.exists(Rm_Mysql):
        logger.error("{0} is not exists".format(Rm_Mysql))
        sys.exit(1)
    for i in ip:
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh.ssh_exec_shell('{0}'.format(Rm_Mysql), '{0}'.format(Rm_Mysql))
        ssh.ssh_exec_cmd("rm -f {0}".format(Rm_Mysql))
        ssh.__del__()


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
    parser = OptionParser("Usage: %prog -s -t -f")
    parser.add_option("-s", dest="server1", action="store", help="server1")
    parser.add_option("-t", dest="server2", action="store", help="server2")
    parser.add_option("-f", "--tarfile", dest="tarfile", action="store",default="/soft/mysql-5.7.20-linux-glibc2.12-x86_64.tar.gz", help="file location")
    fake = ['-s','192.168.118.51:3306:1234','-t','192.168.118.52:3306:123','create']
    options, args = parser.parse_args(fake)
    return options, args


def make_dir(ip, port):
    for i in ip:
        dataport = port[ip.index(i)]
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        rst = ssh.ssh_exec_cmd('ls {0}{1}/data/'.format(Mysql_Data_Dir,dataport))
        if rst != '':
            logger.error("server {0} mysql {1} is already install".format(i, dataport))
            sys.exit(1)
        else:
            ssh.ssh_exec_cmd('mkdir -p {0}'.format(Mysql_App_Dir))
            ssh.ssh_exec_cmd('mkdir -p {0}{1}/data/'.format(Mysql_Data_Dir,dataport))
            ssh.ssh_exec_cmd('mkdir -p {0}{1}/binlog/'.format(Mysql_Log_Dir,dataport))
            ssh.ssh_exec_cmd('mkdir -p {0}{1}/relaylog/'.format(Mysql_Log_Dir,dataport))
            ssh.ssh_exec_cmd('touch {0}{1}/itpuxdb-error.err'.format(Mysql_Log_Dir,dataport))
        ssh.__del__()


def extract(ip, mysqlfile):
    if not os.path.exists(mysqlfile):
        logger.error("{0} is not exists".format(mysqlfile))
        sys.exit(1)
    os.chdir(os.path.dirname(mysqlfile))
    t = tarfile.open(mysqlfile, 'r:gz')
    t.extractall()
    t.close()
    os.system("cd " + mysqlfile.split('.tar.gz')[0] + " ;tar czvf mysql.tar.gz *")
    for i in ip:
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh._upload_file("{0}/mysql.tar.gz".format(mysqlfile.split('.tar.gz')[0]), '/soft/mysql.tar.gz')
        ssh.ssh_exec_cmd('cd {0}'.format(Mysql_App_Dir) + '; tar -zxvf /soft/mysql.tar.gz -C .')
        time.sleep(20)
        ssh.ssh_exec_cmd('rm -f /soft/mysql.tar.gz')
        ssh.__del__()
    os.system("rm -rf " + mysqlfile.split('.tar.gz')[0])


def copyfile(ip,port):
    if not os.path.exists(Init_Conf):
        logger.error("Init mysql conf do not exist,please upload to /soft")
        sys.exit(1)
    for i in ip:
        dataport = port[ip.index(i)]
        srvid = i.split('.')[-1]
        f1 = open('{0}'.format(Init_Conf), 'r',)
        f2 = open('/soft/my{0}{1}.cnf'.format(srvid,dataport), 'w',)
        for line in f1:
            if "3306" in line:
                line = line.replace("3306", "{0}".format(dataport))
            if "server-id" in line:
                line = "server-id={0}{1}\n".format(srvid,dataport)
            if "bind_address" in line:
                line = "bind_address={0}\n".format(i)
            f2.write(line)
        f1.close()
        f2.close()
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh._upload_file('/soft/my{0}{1}.cnf'.format(srvid,dataport),'{0}{1}/my.cnf'.format(Mysql_Data_Dir,dataport))
        os.system('rm -f /soft/my{0}{1}.cnf'.format(srvid,dataport))
        ssh.__del__()

def setowner(ip):
    for i in ip:
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        rst = ssh.ssh_exec_cmd('id mysql')
        if rst == '':
            ssh.ssh_exec_cmd("useradd -M -s /sbin/nologin mysql")
            ssh.ssh_exec_cmd("chown -R mysql:mysql {0}".format(Mysql_Dir))
        else:
            ssh.ssh_exec_cmd("chown -R mysql:mysql {0}".format(Mysql_Dir))
        time.sleep(2)
        ssh.__del__()


def mysqlinstall(ip, port):
    for i in ip:
        dataport = port[ip.index(i)]
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh.ssh_exec_cmd("{0}bin/mysqld --defaults-file=/mysql/data/{1}/my.cnf --initialize --user=mysql --basedir={2} --datadir={3}{4}/data/".format(Mysql_App_Dir, dataport, Mysql_App_Dir, Mysql_Data_Dir, dataport))
        time.sleep(30)
        ssh.__del__()


def setenv(ip):
    for i in ip:
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh.ssh_exec_cmd("echo PATH=$PATH:{0}bin >> ~/.bash_profile".format(Mysql_App_Dir))
        ssh.ssh_exec_cmd("echo 'export PATH' >> ~/.bash_profile")
        ssh.ssh_exec_cmd("source ~/.bash_profile")
        ssh.__del__()


def setscript(ip, port):
    if not os.path.exists(Start_Conf):
        logger.error("Start Mysql conf do not exist,please upload to /soft")
        sys.exit(1)
    for i in ip:
        dataport = port[ip.index(i)]
        srvid = i.split('.')[-1]
        f1 = open('{0}'.format(Start_Conf), 'r',)
        f2 = open('/soft/mysql{0}{1}.server'.format(srvid,dataport), 'w',)
        for line in f1:
            if "3306" in line:
                line = line.replace("3306", "{0}".format(dataport))
            f2.write(line)
        f1.close()
        f2.close()
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        ssh._upload_file('/soft/mysql{0}{1}.server'.format(srvid,dataport),'{0}mysql'.format(Mysql_Start_Dir))
        ssh.ssh_exec_cmd("chmod +x {0}mysql".format(Mysql_Start_Dir))
        os.system('rm -f /soft/mysql{0}{1}.server'.format(srvid,dataport))
        ssh.__del__()


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


def mysqlstart(ip, port, mysqlpwd):
    for i in ip:
        dataport = port[ip.index(i)]
        datapwd = mysqlpwd[ip.index(i)]
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
#        ssh.ssh_exec_cmd("{0}bin/mysqld --defaults-file={1}{2}/my.cnf &".format(Mysql_App_Dir, Mysql_Data_Dir, dataport))
#        time.sleep(12)
        ssh.ssh_exec_cmd("{0}mysql start".format(Mysql_Start_Dir))
        time.sleep(15)
        rst = ssh.ssh_exec_cmd("cat {0}{1}/itpuxdb-error.err |grep 'root@localhost' |awk -F': ' '{2}' |tr -d '\n'".format(Mysql_Log_Dir, dataport, '{print $NF}'))
        ssh.ssh_exec_cmd("{0}bin/mysqladmin -uroot -p'{1}' password '{2}' -S {3}{4}/mysql.sock".format(Mysql_App_Dir, rst, datapwd, Mysql_Data_Dir, dataport))
        ssh.__del__()

def setreplicate(ip, port, mysqlpwd):
    for i in ip:
        dataport = port[ip.index(i)]
        datapwd = mysqlpwd[ip.index(i)]
        ssh = SSHManager(i, '{0}'.format(User), '{0}'.format(Pwd))
        rst = ssh.ssh_exec_cmd("netstat -lntup|grep {0}".format(dataport))
        if rst == '':
            logger.error("Start Mysql failed,Please check")
            sys.exit(1)
        else:
            time.sleep(20)
#            ssh.ssh_exec_cmd('{0}bin/mysql -uroot -p{1} -S {2}{3}/mysql.sock -e "create user {4}@{5} identified by {6}; grant replication slave on {7}@{8}; flush privileges;"'.format(Mysql_App_Dir, datapwd, Mysql_Data_Dir, dataport, "'repuser'", "'%'", "'repuser123'", "*.* to 'repuser'", "'%'"))
            ssh.ssh_exec_cmd('{0}bin/mysql -uroot -p{1} -S {2}{3}/mysql.sock -e "{4}"'.format(Mysql_App_Dir, datapwd, Mysql_Data_Dir, dataport, "create user 'repuser'@'%' identified by 'repuser123';grant replication slave on *.* to 'repuser'@'%';flush privileges;"))
            if ip.index(i) != 0:
                ssh.ssh_exec_cmd('{0}bin/mysql -uroot -p{1} -S {2}{3}/mysql.sock -e "change master to '.format(Mysql_App_Dir, datapwd, Mysql_Data_Dir, dataport) + "master_host='{0}',master_port={1},master_user='{2}',master_password='{3}',master_auto_position=1;".format(ip[0], port[0], RelUser, RelPwd) + '"')
                time.sleep(2)
                rst = ssh.ssh_exec_cmd('{0}bin/mysql -uroot -p{1} -S {2}{3}/mysql.sock -e "reset slave;start slave;show slave status\G"'.format(Mysql_App_Dir, datapwd, Mysql_Data_Dir, dataport))
                print(rst)
                ssh.__del__()


if __name__ == '__main__':
    mysqlip = []
    mysqlport = []
    mysqlpwd = []

    install_log()
    options, args = opt()
    try:
        cmd = args[0]
    except IndexError:
        print("%s follow a command" % __file__)
        print("%s -h" % __file__)
        sys.exit(1)

    if (options.tarfile and os.path.isfile(options.tarfile)):
        mysqlfile = options.tarfile

    if (options.server1):
        count = len(options.server1.split(':'))
        if count == 3:
            ip = options.server1.split(':')[0]
            port = options.server1.split(':')[1]
            pwd = options.server1.split(':')[2]
            if os.system('ping -c 3 {0}'.format(ip)) or not str.isdigit(port) or not pwd:
                logger.error("请检查网路连通性、端口号、密码!")
                sys.exit(1)
            else:
                mysqlip.append(ip)
                mysqlport.append(port)
                mysqlpwd.append(pwd)
        else:
            print("%s -h" % __file__)
            sys.exit(1)

    if (options.server2):
        count = len(options.server2.split(':'))
        if count == 3:
            ip = options.server2.split(':')[0]
            port = options.server2.split(':')[1]
            pwd = options.server2.split(':')[2]
            if os.system('ping -c 3 {0}'.format(ip)) or not str.isdigit(port) or not pwd:
                logger.error("请检查网路连通性、端口号、密码!")
                sys.exit(1)
            else:
                mysqlip.append(ip)
                mysqlport.append(port)
                mysqlpwd.append(pwd)
        else:
            print("%s -h" % __file__)
            sys.exit(1)

    if cmd == 'create':
#        rm_mysql(mysqlip)
#        logger.info('step1:RmMysql completed')
#
#        make_dir(mysqlip, mysqlport)
#        logger.info('step2:makeDIR completed')
#        time.sleep(5)
#
#        extract(mysqlip, mysqlfile)
#        logger.info('step3:extract completed')
#
#        copyfile(mysqlip,mysqlport)
#        logger.info('step4:copyFile completed')#
#
#        setowner(mysqlip)
#        logger.info('step5:setOwner completed')
#
#        mysqlinstall(mysqlip, mysqlport)
#        logger.info('step6:mysql_install completed')
#        time.sleep(300)
#
#        setenv(mysqlip)
#        logger.info('step7:setEnv completed')
#
#        #        checkinstall(mysqlport)
#        #        logger.info('step9:checkInstall completed')
#        setscript(mysqlip, mysqlport)
#        logger.info('step8:setScripts completed')
#
#        mysqlstart(mysqlip, mysqlport, mysqlpwd)
#        logger.info('step9:mysqlserviceStart completed')

        setreplicate(mysqlip, mysqlport, mysqlpwd)
        logger.info('step10:setReplicate completed')
#
#        print('mysql install finish')




