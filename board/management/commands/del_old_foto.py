# -*- coding: utf-8 -*-
import os 
import shutil
import time

from board.models import Photo
from django.core.exceptions import ObjectDoesNotExist
from realtyboard.settings import MEDIA_ROOT




def del_foto():
    pop = 0
    files = os.listdir(MEDIA_ROOT)
    for file in files:
        if len(file) == 2:
            print '-----------------------------------------------'
            print file
            pop = int(pop) + 1
            print pop
            print '-----------------------------------------------'
            path = os.path.join(MEDIA_ROOT,file)
            for i in os.listdir(path):
                photo = os.path.join(path,i)
                date = os.path.getctime(photo)
                date_tim = time.gmtime(date).tm_year
                if date_tim < 2016:
                    try:
                        print "!!!!!!!!!!!!!!!!!"
                        print date_tim
                        print "!!!!!!!!!!!!!!!!!"
                        os.remove(photo)
                    except OSError:
                        shutil.rmtree(photo)






def del_foto_not_url():
    ik = 0
    ir = 0
    phot = Photo.objects.all()
    pop = 0
    files = os.listdir(MEDIA_ROOT)
    for file in files:
        if len(file) == 2:
            print '-----------------------------------------------'
            print file
            pop = int(pop) + 1
            print pop
            print '-----------------------------------------------'
            path = os.path.join(MEDIA_ROOT,file)
            for i in os.listdir(path):
                photo =  os.path.join(file,i)
                if phot.filter(photo = photo):
                    ir = ir + 1
                else:
                    ik = ik + 1
                print ir 
                print (ik, u'Без сылки' )
                print '------------------------------------'

ik = 0
ir = 0
phot = Photo.objects.all()
file = '00'
path = os.path.join(MEDIA_ROOT,file)
for i in os.listdir(path):
    photo =  os.path.join(file,i)
    if phot.filter(photo = photo):
        ir = ir + 1
    else:
        print ir 
        print ik, u'Без сылки' 
        print '------------------------------------'



class Command(BaseCommand):

    def handle(self, *args, **options):
        o = del_foto()
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')