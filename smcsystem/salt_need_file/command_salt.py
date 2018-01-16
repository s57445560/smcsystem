#/usr/bin/python
#--coding:utf-8--


import salt.client
import sys,json
import os
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='test.log',
                    filemode='w')

class Salt_client(object):
    def __init__(self):
        self.local = salt.client.LocalClient()

    def swith(self,hosts1,file_path):
        hosts1 = hosts1.split(',')
        file_path1 = file_path.split('/')
        file_path1.pop()
        file_path1 = '/'.join(file_path1)
        return hosts1,file_path1



class Update(Salt_client):
    '''
    #主机
    hosts = sys.argv[1]
    #原文件路径
    file_path = sys.argv[3]
    #程序名称
    app_name = sys.argv[2]
    #新包存放了路径
    app_path = sys.argv[4]
    #启动命令
    command = sys.argv[5]'''
    def  file_chekc(self,hosts1,direct):
         # local = salt.client.LocalClient()
         result = self.local.cmd(hosts1,'cmd.run',['ls %s'%direct],expr_form='list')
         for i in hosts1:
            if i in result.keys:
                result[i] = "salt_log_error"
         f_list = []
         for k,v in result.items():
      #      print(k,v)
            if "No such file or directory" in v:
                f_list.append(k)
         if len(f_list) > 0:
            sys.exit("%s路径不存在%s" %(f_list,direct))
    def pro_update(self,hosts,app_name,file_path,app_path,command):
        hosts1 = self.swith(hosts,file_path)[0]
        file_path1 = self.swith(hosts,file_path)[1]
        self.file_chekc(hosts1,file_path)
        self.file_chekc(hosts1,app_name)
        try:
            result1 = self.local.cmd(hosts1,'cmd.script',['salt://scripts/pro_update.sh','%s %s %s %s "%s"' %(app_name,file_path,app_path,file_path1,command)],expr_form='list')
        except Exception as e:
            logging.error(e)
        else:
            print(app_name,file_path,app_path,command,file_path1)
            logging.info(result1)
	data = json.dumps(result1)
        print(data)

class Command(Salt_client):
    def orders(self,hosts1,command):
        import re
        p = re.compile(r"^tail -")
        m = p.search(command)
        hosts1 = hosts1.split(',')
        if not m:
	    li = ['rm','top','sar','nvidia','watch','stat','iostat']
	    for i in li:
                if  i in command:
                    print(json.dumps({"error":"true","message":u"无法执行此操作!"}))
                    sys.exit('危险操作')
        try:
            result1 = self.local.cmd(hosts1,'cmd.run',['%s'%command],expr_form='list')
        except Exception as e:
            logging.error(e)
        else:
            logging.info(result1)
        for i in hosts1:
            if i not in result1:
                result1[i] = "salt_log_error"
        data = json.dumps(result1)
	print(data)
        return data

class Rollback(Salt_client):
    def roll(self,hosts,app_name,file_path,command):
            hosts1 = self.swith(hosts,file_path)[0]
            file_path1 = self.swith(hosts,file_path)[1]
            try:
                result1 = self.local.cmd(hosts1,'cmd.script',['salt://salt.sh','%s %s %s  "%s"' %(app_name,file_path,file_path1,command)],expr_form='list')

            except Exception as e:
                logging.error(e)
            else:
                logging.info(result1)
            for i in hosts1:
                if i not in result1.keys:
                    result1[i] = "salt_log_error"
            data = json.dumps(result1)
            print(data)


c = Command()
hosts1 = sys.argv[1]
command = sys.argv[2]
c.orders(hosts1,command)
#result = c.orders("192.168.2.161,192.168.2.162","ls")
#print(result)
