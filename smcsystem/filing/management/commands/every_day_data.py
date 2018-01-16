#!/usr/bin/python
from django.core.management.base import BaseCommand, CommandError
from client import running

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    #必须实现的方法
    def handle(self, *args, **options):
        running.run()
        self.stdout.write('Successfully run')
