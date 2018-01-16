#!/usr/bin/python
# author:sunyang

import os
import settings
import smcapi,get_info
import json
import print_log
import logging
import tes
from datetime import datetime



class Run_code(object):
    def __init__(self):
        self.put_list = []
        self.post_list = []
        self.delete_list = []
        self.err_list = []
        self.salt_command_ip_list = []
        self.status = True
        self.socket_api = smcapi.Api()
        self.web_ip_list = []
        self.ip_data = self.socket_api.get()
        self.log = print_log.Log(logname=os.path.join(settings.BASE_DIR,"logs/smc.log"), logger="smc_client", level=logging.INFO).getlog()
        try:
            self.ssh = get_info.Go_ssh(settings.SALT_IP, settings.PASSWD)
        except:
            print("salt connect error")
            self.log.error(u"Salt server connect fail! Check that the settings to configure is correct.")
            exit(1)
        for ip in self.ip_data.json():
            self.web_ip_list.append(ip.get('salt_id'))
        if os.path.exists(settings.LOG_PATH):
            os.remove(settings.LOG_PATH)


    def run_salt(self):
        try:
            self.ssh.run("salt '*' cmd.script salt://scripts/get_host_info.sh >/tmp/test.log")
            self.ssh.run("cat /tmp/test.log|grep -Po '[\d\.]+\|.*' >/tmp/host.log")
            self.salt_all_ip = self.ssh.run("salt-key -L|sed -n '/Accepted Keys/,/Denied Keys/p'|egrep -v '(^Accepted Keys:|^Denied Keys:)'|sed ':a;N;s/\\n/,/;ta'")
            self.ssh.ssh_get()
            self.ssh.ssh_close()
        except:
            print('salt command error')
            self.log.error(u"Salt server execute command fail!")
            self.status = False
            return False

        salt_ip = str(self.salt_all_ip, encoding="utf-8").strip('\n').split(",")
        if os.path.exists(settings.LOG_PATH):
            with open(settings.LOG_PATH,"r",encoding="utf-8") as f:
                for file_line in f:
                    salt_id = file_line.split("|")[14].rstrip("\n")
                    # 判断是否是在get列表里 如果在就是更新put，不再就是post添加
                    if salt_id in self.web_ip_list:
                        self.put_list.append(file_line)
                    else:
                        self.post_list.append(file_line)
                    self.salt_command_ip_list.append(salt_id)
            print(salt_ip)
            for web_ip in self.web_ip_list:
                if web_ip not in salt_ip:
                    print("----------not salt",web_ip)
                    self.delete_list.append(web_ip)
            print("salt_ip",salt_ip)
            print("salt_command_ip_list",self.salt_command_ip_list)
            print("post_list",self.post_list)
            print("put_list",self.put_list)
            self.err_list = list(set(salt_ip) - set(self.salt_command_ip_list))
        else:
            return False


    def send_host_info(self):
        self.run_salt()

        print(self.post_list)
        print(self.put_list)
        print(self.delete_list)
        print(self.err_list)
        for i in self.err_list:
            self.log.warning(u"Salt command execute %s fail!" % i.split("|")[0])
            self.socket_api.delete({"err": json.dumps(i), "status": self.status})

        for i in self.delete_list:
            self.log.info(u"Set to %s Offline!" % i.split("|")[0])
            self.socket_api.delete({"data": json.dumps(i), "status": self.status})

        # self.socket_api.delete({"data": json.dumps(self.put_list), "status": self.status})
        for i in self.post_list:
            print("-----------------post")
            self.log.info(u"Add to %s success!"% i.split("|")[0])
            self.socket_api.post({"data":json.dumps(i),"status":self.status})
        for i in self.put_list:
            print("-----------------put")
            self.log.info(u"Update to %s success!" % i.split("|")[0])
            self.socket_api.put({"data":json.dumps(i),"status":self.status})



def run():
    go = Run_code()
    go.send_host_info()



if __name__ == '__main__':
    run()
