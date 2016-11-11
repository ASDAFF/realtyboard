# -*- coding: utf-8 -*-
import os 
import re
from time import time

# from personal.models import UserData
from board.models import Advert
from django.core.management.base import BaseCommand, CommandError
from realtyboard.settings import PROJECT_PATH, MEDIA_ROOT




def avers():
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/avers')
    f = open('%s/%s' % (temp_dir, 'avers.txt'),'r') 
    for i, line in enumerate(f):
        login = re.findall(r'[^\:]*', line)
        advert = Advert.objects.filter(author__username = login[0])
        for i in advert:
            i.raw_phones = '0671584000'
            i.save()
        print login[0]
        print "Login %s" %(i)
    f.close()






class Command(BaseCommand):

    def handle(self, *args, **options):
        o = avers()
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')