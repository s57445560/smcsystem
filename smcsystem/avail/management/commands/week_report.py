#!/usr/bin/python
from django.core.management.base import BaseCommand, CommandError
from smcsystem import settings
from avail.models import Info
import time
import datetime
from avail import send_mail

new_day = time.strftime("%Y-%m-%d")

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    # 必须实现的方法
    def handle(self, *args, **options):
        objs = []
        if settings.AUTO_REPORT:
            result = True
            today = datetime.date.today()
            for i in range(7):
                day = today - datetime.timedelta(days=i)
                obj = Info.objects.filter(start_time__contains=day.strftime('%Y-%m-%d'))
                objs.extend(list(obj))
            surplus = Info.objects.filter(end='2')
            set_objs = set(objs) - set(surplus)
            result = send_mail.run(set_objs,surplus,"值班故障周报")
            if not result:
                send_mail.run(set_objs,surplus,"值班故障周报")
            
            self.stdout.write('Successfully run')
        else:
            self.stdout.write('auto_report false!')
