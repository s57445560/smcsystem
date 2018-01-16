import paramiko
from smcsystem import settings
class Go_ssh(object):
    def __init__(self,ip=settings.SALT_IP,passwd=settings.SALT_PASSWD, user='root',port=22):
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
        return result

    def ssh_close(self):
        self.ssh.close()