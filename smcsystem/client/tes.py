#!/usr/bin/python
# coding=utf-8
# author: sunyang

import sys,os
from django.core.wsgi import get_wsgi_application
sys.path.extend(['smcsystem',])
os.environ.setdefault("DJANGO_SETTINGS_MODULE","smcsystem.settings")
application = get_wsgi_application()
from filing import models

def set_db_history():
    group_id = models.Group.objects.all().values("id","name")
    for id in group_id:
        disk_all = 0
        disk_use = 0
        b1 = models.Group.objects.get(id=id['id'])
        disk_list_data = b1.host_set.filter(status=1, type__in=[1, 2]).values("disk_use", "disk_capacity")
        for obj in disk_list_data:
            if obj["disk_use"] != None:
                disk_use += float(obj["disk_use"].strip("g"))
        models.Group_disk_history.objects.create(disk_num=disk_use,group_id=id['id'])








