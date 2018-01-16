import paramiko

# 创建SSH对象
ssh = paramiko.SSHClient()
# 允许连接不在know_hosts文件中的主机
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接服务器
ssh.connect(hostname='192.168.2.182', port=22, username='root', password='ohpFA^XB1vyavEvJy!')

# 执行命令
# stdin, stdout, stderr = ssh.exec_command("""salt-key -L|sed -n '/Accepted Keys/,/Denied Keys/p'|grep -Po '[\d.]+'|sed ':a;N;s/\n/,/;ta'""")
stdin, stdout, stderr = ssh.exec_command("""salt-key -L|sed -n '/Accepted Keys/,/Denied Keys/p'|grep -Po '[\d.]+'|sed ':a;N;s/\\n/,/;ta'""")
# 获取命令结果
result = stdout.read()

for i in str(result).split(","):
    print(i)
print(result)
# 关闭连接
ssh.close()