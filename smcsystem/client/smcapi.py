#!/usr/bin/python
# author: sunyang

import requests
import json
import time, hashlib
from client import settings

class Api(object):

    def __init__(self):
        self.api_url = settings.APIURL

    def md5(self,appid):
        new_time = str(time.time())
        m = hashlib.md5()
        m.update(bytes(appid + new_time,encoding='utf-8'))
        return m.hexdigest(),new_time

    def get_key(self):
        self.data, self.client_time = self.md5(settings.APPID)
        self.new_appid = "%s|%s" % (self.data, self.client_time)

    # 获取
    def get(self):
        self.get_key()
        result = requests.get(url=self.api_url,
                         headers={'appid':self.new_appid })
        return result
        print(result.json())

    # 删除
    def delete(self,data):
        self.get_key()
        a = requests.delete(url=self.api_url,
                         headers={'appid':self.new_appid },
                            params=data)
        print(a.json())
        return a

    # 更新
    def put(self,data):
        self.get_key()
        result = requests.put(url=self.api_url,
                         headers={'appid':self.new_appid },
                        params=data)
        print(result.json())
        return result

    # 添加
    def post(self,data):
        self.get_key()
        a = requests.post(url=self.api_url,
                         headers={'appid':self.new_appid },
                          data=data)
        print(a.json())

# a = Api()
# a.get()
# a.put({'info':['192.168.2.2']})
