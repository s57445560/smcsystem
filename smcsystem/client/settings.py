#!/usr/bin/python

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(BASE)
from smcsystem.settings import SALT_IP,SALT_PASSWD

# 用来配置salt的地址，远程控制salt来抓取数据

SALT_IP = SALT_IP
PASSWD = SALT_PASSWD

# 配置 api 验证

APPID = 'lgxy@smc_host_api'

# salt抓取的 日志路径

LOG_PATH = os.path.join(BASE_DIR,"logs/host.log")

# api url

APIURL = "http://127.0.0.1:80/api/host/"

print(SALT_PASSWD)