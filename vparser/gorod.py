# -*- coding: utf-8 -*-
import datetime
from  board.models import Advert, City, Phone
import os
from django.utils import timezone
from django.core.mail import EmailMessage
import re

#  //нежилая аренда 066
# //продажа нежилого фонда 033
# //жилая аренда 052
# //клиенты 053
# //жилая продажа квартиры 070
# //продажа дома участки 165
cats = {
    11 : '070' , #  prodam-kvartiru
    12 : '070' , #  prodam-gostinku-komnatu
    14 : '165' , #  prodam-dom
    16 : '165' , #  prodam-uchastok
    17 : '033' , #  prodam-kommercheskuyu-nedvizhimost
    21 : '052' , #  sdam-kvartiru
    22 : '052' , #  sdam-gostinku-komnatu
    24 : '052' , #  sdam-dom
    26 : '066' , #  sdam-uchastok
    27 : '066' , #  sdam-kommercheskuyu-nedvizhimost
    31 : '053' , #  kuplyu-kvartiru
    32 : '053' , #  kuplyu-gostinku-komnatu
    34 : '053' , #  kuplyu-dom
    36 : '053' , #  kuplyu-uchastok
    37 : '053' , #  kuplyu-kommercheskaya-nedvizhimost
    41 : '053' , #  snimu-kvartiru
    42 : '053' , #  snimu-gostinku-komnatu
    44 : '053' , #  snimu-dom
    46 : '053' , #  snimu-uchastok
    47 : '053' , #  snimu-kommercheskuyu-nedvizhimost
}

date_file_name  = timezone.now().strftime('%d.%m')
date_file_name_archives  = 'express-%s.zip' % timezone.now().strftime('%d.%m.%y')

GOROD_PATH = '/data/web/media/uploads/kharkov/gorod/%s'


def gorod():
    two_hours = timezone.now() - datetime.timedelta(hours=3)
    slando_kharkov = open(GOROD_PATH % date_file_name, 'w')
    for string in Advert.objects.filter\
            (
                city_id=20,
                date_of_update__gte=two_hours,
                site='http://kharkov.kha.slando.ua/nedvizhimost'
            ).order_by('-creation_date'):
            # .order_by('-creation_date')


        slando_kharkov.write(
            cats[string.category_id]
            +string.main_text[:255].encode('utf-8')
            +' тел:'+string.get_phone_with_null_str()
            +"\r\n"
        )
    slando_kharkov.close()

    # convert_to_cp_866
    text_in_utf8 = open(GOROD_PATH % date_file_name, 'rb').read()
    text_in_unicode = text_in_utf8.decode('utf8', 'ignore')
    text_in_cp_866 = text_in_unicode.encode('CP866', 'ignore')
    open(GOROD_PATH % date_file_name, 'wb').write(text_in_cp_866)



    make_rar = 'zip -j /data/web/media/uploads/kharkov/gorod/%s -j /data/web/media/uploads/kharkov/gorod/%s' % (date_file_name_archives, date_file_name)
    os.system(make_rar)


    msg = EmailMessage('Рассылка от ЦентрИнформ, тестовый файл', 'рассылка за '+str(timezone.now()), 'centrinform@ci.ua', ['an_gorod@mail.ru'])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.attach_file(GOROD_PATH % date_file_name_archives)
    msg.send()
    #an_gorod@mail.ru


    # .exclude(seller__in=seller):
    ## category_id__in=adv_category_list[category_file_name],