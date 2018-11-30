
import os
import paramiko
import Crypto
from functools import wraps
from datetime import datetime


def timethis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(func.__name__, end - start)
        return result

    return wrapper


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
            self._ssh.connect(hostname=self._host, port=22, username=self._usr, password=self._passwd, timeout=5)
        except Exception:
            raise RuntimeError(
                "ssh connect to [host:{0}, usr:{1}, passwd:{2} faile]".format(self._host, self._usr, self._passwd))

    def _exec_commnad(self, cmd):
        try:
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            return stdout.read().decode()
        except Exception as e:
            raise RuntimeError('Exec command [%s] failed' % str(cmd))

    def ssh_exec_cmd(self, cmd, path='~'):
        try:
            result = self._exec_commnad('cd ' + path + ';' + cmd)
            print(path)
            print(result)
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    @staticmethod
    def is_shell_file(file_name):
        return file_name.endswith('.sh')

    @staticmethod
    def is_file_exit(file_name):
        try:
            with open(file_name, 'r'):
                return True
        except Exception as e:
            return False

    @timethis
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

    def ssh_exec_shell(self, local_file, remote_file, exec_path):
        try:
            if not self.is_file_exit(local_file):
                raise RuntimeError("File {0} not exist".format(local_file))
            if not self.is_shell_file(local_file):
                raise RuntimeError("File {0} is not a shell file".format(local_file))

            self._check_remote_file(local_file, remote_file)

            result = self._exec_commnad('chmod +x ' + remote_file + '; cd ' + exec_path + ';/bin/bash ' + remote_file)
            print('exec shell result: ', result)
        except Exception as e:
            raise RuntimeError("ssh exec shell failed {0}".format(str(e)))


if __name__ == '__main__':
    ip = '192.168.118.51'
    usr = 'root'
    passwd = 'rootroot'
    ssh = SSHManager(ip, usr, passwd)
    ssh.ssh_exec_cmd('ls -l', path='/etc/')
    ssh.ssh_exec_shell('/soft/a.sh', '/soft/a.sh', '/root/')
