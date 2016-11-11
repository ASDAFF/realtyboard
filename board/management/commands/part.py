# -*- coding: utf-8 -*-

import datetime, os, re, time, urllib
from django.core.mail import EmailMessage, send_mail

from board.models import Phone
from personal.models import UserMessage
from realtyboard.settings import MEDIA_ROOT

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time

def part(part):  
    """создание архива для скачивания, первая часть, part обозначает номер части базы,
       тут не используется пока"""
    if not os.path.exists(MEDIA_ROOT+'/base_files/temp'):
        os.makedirs(MEDIA_ROOT+'/base_files/temp')
    date = datetime.datetime.now()
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/temp')
    
    os.system('rm -r %s/*' % temp_dir) # очищаем временный каталог
    
    premier_categories = {
        'rent_comest': ('006', '022', '023', '024', '025', '026', '027', '029'),
        'sale_comest': ('033', '034', '035', '036', '037', '039', '040', '045', 
                        '046', '047', '048'),
        'rent_house_flat': ('052', '054', '055', '056', '057', '058', '059'),
        'sale_flat': ('070', '075', '081', '082', '083', '084', '085', '086', '087',
                      '088', '089', '090', '091', '092', '095', '101', '102', '103', 
                      '104', '105', '106', '107', '108', '109', '110', '111', '112', 
                      '123', '124', '125', '126', '127', '128', '129', '130', '131', 
                      '132', '135', '141', '142', '143', '144', '145', '146', '147', 
                      '148', '149', '150', '151', '152', '155', '160'),
        'sale_house': ('165', '166', '170', '171', '172', '173', '174', '175', '176', 
                       '177', '178', '179', '181', '182', '191'),
        'clients': ('053', '061', '062', '063', '064', '066', '067', '068'),
        'stop_reading': ('195', '197', '202', '205'),
    }

    if date.weekday() == 0:
        pan = 'djs'
    else:
        pan = 'express'
    resp_obj = urllib.urlretrieve(
        'http://premier.ua/rass/%s-%s.zip' % (pan, date.strftime('%d.%m.%y')),
        '%s/%s_premier.zip' % (temp_dir, date.strftime('%Y.%m.%d'))
    )

    if resp_obj[1].type == 'application/x-zip-compressed':
        os.system('unzip %s -d %s' % (resp_obj[0], temp_dir))
        source_file = open('%s/%s' % (temp_dir, date.strftime('%d_%m')))
        str_list = source_file.readlines()
        file_names_list = {
            'rent_comest_hoz': '%s/Hoz/MnfRent_Hoz_%s.txt',
            'rent_comest_vse': '%s/Vse/MnfRent_%s.txt',
            'sale_comest_hoz': '%s/Hoz/Mnf_Hoz_%s.txt',
            'sale_comest_vse': '%s/Vse/Mnf_%s.txt',
            'rent_house_flat_hoz': '%s/Hoz/Rent_Hoz_%s.txt',
            'rent_house_flat_vse': '%s/Vse/Rent_%s.txt',
            'sale_flat_hoz': '%s/Hoz/Flat_Hoz_%s.txt',
            'sale_flat_vse': '%s/Vse/Flat_%s.txt',
            'sale_house_hoz': '%s/Hoz/House_Hoz_%s.txt',
            'sale_house_vse': '%s/Vse/House_%s.txt',
            'clients_hoz': '%s/Hoz/Clients_Hoz_%s.txt',
            'clients_vse': '%s/Vse/Clients_%s.txt',
        }
        if not os.path.exists(temp_dir+'/Hoz'):
            os.makedirs(temp_dir+'/Hoz')
        if not os.path.exists(temp_dir+'/Vse'):
            os.makedirs(temp_dir+'/Vse')
        files_list = {}
        try:
            for key in file_names_list:
                files_list[key] = open(file_names_list[key] % 
                    (temp_dir, date.strftime('%Y.%m.%d_%H.%M')), 'w') 
            stop_reading = False
            count = 0
            for st in str_list:
                count += 1
                category = st[0:3]
                st = st.decode('866')[4:]
                author = check_phones(st)
                if author == 'no phone':
                    continue
                st = st[:-2] + u' [Премьер]\r\n'
                if len(st) > 255: # если строка больше 255 символов то ее нужно укоротить
                    match = re.search(r'(?:\d{3}-\d{2,3}-\d{2,3}(?:-\d{2,3})?)|(?:\d{10})', st)
                    st = st[:match.start()-len(st)+253] + '; ' + st[match.start():]
                for key in premier_categories:
                    if category in premier_categories[key]:
                        if key == 'stop_reading':
                            stop_reading = True
                        else:
                            files_list[key+'_vse'].write(st.encode('cp1251', 'ignore'))
                            if author == 'owner' or author == 'undefined':
                                files_list[key+'_hoz'].write(st.encode('cp1251', 'ignore'))
                if stop_reading:
                    break   
        finally:
            for key in files_list: # закрываем все файлы
                files_list[key].close()
            os.system('rar d %(media)s/base_files/rar/kharkov/%(year)s/%(date)s_1_chast.rar' % {
                'media': MEDIA_ROOT, 
                'year': date.strftime('%Y'), 
                'date': date.strftime('%Y.%m.%d'),
            })
            os.system('rar a -ep1 %(media)s/base_files/rar/kharkov/%(year)s/%(date)s_1_chast.rar \
                      %(temp)s/Hoz %(temp)s/Vse' % {'media': MEDIA_ROOT, 
                                                    'year': date.strftime('%Y'), 
                                                    'date': date.strftime('%Y.%m.%d'),
                                                    'temp': temp_dir}
            )
    else:
        send_mail(u'НЕ ВЫШЛА ПЕРВАЯ ЧАСТЬ, перезапустить когда заработает премьер.',
            u'Ручной запуск первой части: "python manage.py part 1"'+' time: '+datetime.datetime.now().strftime('%H:%M'),
            'support@ci.ua', ['1centrinform@gmail.com'], fail_silently=False)


def check_phones(string):
    phone_list = re.findall(r'(?:\d{3}-\d{2,3}-\d{2,3}(?:-\d{2,3})?)|(?:\d{10})', string)
    if phone_list:
        for phone in phone_list:
            phone = int(re.sub(r'\D', '', phone))
            try:
                ph_obj = Phone.objects.get(phone=phone)
                if ph_obj.agent in (1, 2, 5):
                    return 'agent'
                elif ph_obj.agent in (3, 4):
                    return 'owner'
            except Phone.DoesNotExist:
                pass
        return 'undefined'
    else:
        return 'no phone'    


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--part',
                    action='store_true',
                    dest='pat',
                    default=False,
                    help='part'),
    )

    def handle(self, *args, **options):
        t1 = time()
        part(args[0])
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')
