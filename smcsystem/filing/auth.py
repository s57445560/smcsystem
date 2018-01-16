#! /usr/bin/python
# coding:utf-8
# author: sunyang
# api validate
from django.shortcuts import HttpResponse
import json
import time
import hashlib
import copy

APPID_LIST = {}
APPID = 'lgxy@smc_host_api'

DEL_ID = []

def md5(appid,new_time):
    m = hashlib.md5()
    m.update(bytes(appid + new_time,encoding='utf-8'))
    return m.hexdigest()


def auth_status(request):
    DEL_ID = []
    api_id = request.META.get('HTTP_APPID')
    try:
        appid_md5, client_time = api_id.split('|')
    except:
        return False
    local_time = time.time()
    float_client_time = float(client_time)
    if local_time - 10 > float_client_time:
        return False

    for id in APPID_LIST.keys():
        if local_time - 20 > APPID_LIST[id]:
            DEL_ID.append(id)
    for id in DEL_ID:
        del APPID_LIST[id]
        print('del---------------')
    if api_id in APPID_LIST:
        return False

    local_md5 = md5(APPID, client_time)
    if appid_md5 == local_md5:
        APPID_LIST[api_id] = float_client_time
        return True
    else:
        return False


def apiauth(func):
    def para(*args, **kwargs):
        request = args[1]
        result = auth_status(request)
        if not result:
            return HttpResponse(json.dumps({'code':'1001','message':'auth fail'}))
        return func(*args, **kwargs)
    return para