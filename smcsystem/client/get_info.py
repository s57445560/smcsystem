#!/usr/bin/python
# author: sunyang
import paramiko
from client import settings




class Go_ssh(object):
    def __init__(self,ip,passwd, user='root',port=22):
        self.port = port
        self.user = user
        self.ip = ip
        self.passwd = passwd
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=self.ip, port=self.port, username=self.user, password=self.passwd)

    def run(self,command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        result = stdout.read()
        print(result)
        return result

    def ssh_close(self):
        self.ssh.close()

    def ssh_get(self):
        transport = paramiko.Transport((self.ip, self.port))
        transport.connect(username=self.user, password=self.passwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get('/tmp/host.log', settings.LOG_PATH)
        transport.close()

# a = Go_ssh(settings.SALT_IP,settings.PASSWD)
# a.run('pwd')
# a.ssh_get()