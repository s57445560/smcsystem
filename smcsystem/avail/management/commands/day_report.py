#!/usr/bin/python
from django.core.management.base import BaseCommand, CommandError
from smcsystem import settings
from avail.models import Info
import time
from avail import send_mail

new_day = time.strftime("%Y-%m-%d")

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    # 必须实现的方法
    def handle(self, *args, **options):
        if settings.AUTO_REPORT:
            result = True
            objs = Info.objects.filter(start_time__contains=new_day)
            surplus = Info.objects.filter(end='2')
            set_objs = set(objs) - set(surplus)
            #result = send_mail.run(set_objs,surplus,"值班故障日报")
            if not result:
                send_mail.run(set_objs,surplus,"值班故障日报")
            
            self.stdout.write('Successfully run')
        else:
            self.stdout.write('auto_report false!')
