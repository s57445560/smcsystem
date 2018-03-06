#!/usr/bin/python
# coding=utf8

import sys,os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE)
from django.core.wsgi import get_wsgi_application
sys.path.extend(['smcsystem',])
# 在其他程序中配置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE","smcsystem.settings")
application = get_wsgi_application()

# 导入需要操作的模块
from avail import models
import send_mail

run_date = "2018-03-05"


print(models.Info.objects.filter())
objs = models.Info.objects.filter(start_time__contains=run_date)
surplus = models.Info.objects.filter(end='2')
set_objs = set(objs) - set(surplus)
send_mail.run(set_objs,surplus,"值班故障日报")
