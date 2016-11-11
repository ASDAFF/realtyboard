# -*- coding: utf-8 -*-
import datetime, re, os
from board.models import Advert, City, Phone
from django.utils import timezone

from realtyboard.settings import MEDIA_ROOT

def moroz():
    two_day = timezone.now() - datetime.timedelta(days=2)  # two days ago

    list_of_city = [8, 20]

    adv_category_list ={
        'Rent_Hoz_'   : [21, 22, 24],
        'Flat_Hoz_'   : [11, 12],
        'House_Hoz_'  : [14, 16],
        'MnfRent_Hoz_': [27],
        'Mnf_Hoz_'    : [17],
        'Client_Hoz_' : [41, 42, 44, 46, 47, 31, 32, 34, 36,37],
        'Rent_'       : [21, 22, 24],
        'Flat_'       : [11, 12],
        'House_'      : [14, 16],
        'MnfRent_'    : [27],
        'Mnf_'        : [17],
        'Client_'     : [41, 42, 44, 46, 47, 31, 32, 34, 36,37],
        }

    for city in City.objects.filter(id__in=list_of_city):
        for category_file_name in adv_category_list:

            destination_folder = re.findall(r'_(.*?)_', category_file_name)
            if destination_folder:
                if destination_folder[0] == 'Hoz':
                    destination_folder = 'Hoz'
                    seller = [1,2,5]
            else:
                destination_folder = 'Vse'
                seller = []

            second_base_path = '%(base_files)s/%(city)s/%(year)s/%(date_folder_name)s/%(folder_type)s' %\
            {
                'base_files': os.path.join(MEDIA_ROOT, 'base_files'),
                'city': city.slug,
                'year':datetime.datetime.now().year,
                'date_folder_name':datetime.datetime.utcnow().strftime("%d.%m.%Y_2_chast"),
                'folder_type':destination_folder,
            }

            if not os.path.exists(second_base_path):
                os.makedirs(second_base_path)

            file_base = open('%(base_files)s/%(city)s/%(year)s/%(date_folder_name)s/%(folder_type)s/%(category_file_name_with_date)s.txt' %\
            {
                'base_files': os.path.join(MEDIA_ROOT, 'base_files'),
                'city': city.slug,
                'year':datetime.datetime.now().year,
                'date_folder_name':datetime.datetime.utcnow().strftime("%d.%m.%Y_2_chast"),
                'folder_type':destination_folder,
                'category_file_name_with_date':category_file_name+datetime.datetime.utcnow().strftime("%Y.%m.%d_5.10"),
            }
                             ,'w')
            for string in Advert.objects.filter(
                    city=city,
                    date_of_update__gte=two_day,
                    category_id__in=adv_category_list[category_file_name],
            # ).exclude(seller__in=seller):
            ).exclude(phone__agent__in=seller):

                file_base.write(
                    string.main_text[:200].encode('utf-8')
                    + ' тел:'+string.get_phone_with_null_str()
                    + (string.site.encode('utf-8') if string.site else 'ci.ua')
                    + "\r\n"
                )
            file_base.close()

            #convert_to_cp_1251
            text_in_utf8 = open(file_base.name, 'rb').read()
            text_in_unicode = text_in_utf8.decode('utf8', 'ignore')
            text_in_cp1251 = text_in_unicode.encode('cp1251', 'ignore')
            open(file_base.name, 'wb').write(text_in_cp1251)




        path_rar = '%(rar_files)s/%(city)s/%(year)s' % {
            'rar_files': os.path.join(MEDIA_ROOT, 'base_files/rar'),
            'city': city.slug, 
            'year': datetime.datetime.now().year
        }
        if not os.path.exists(path_rar):
            os.makedirs(path_rar)

        make_rar = 'rar a -ep1 %(rar_files)s/%(city)s/%(year)s/%(archiv_name)s %(base_files)s/%(city)s/%(year)s/%(date_folder_name)s' % \
        {
            'rar_files': os.path.join(MEDIA_ROOT, 'base_files/rar'),
            'base_files': os.path.join(MEDIA_ROOT, 'base_files'),
            'city': city.slug,
            'year':datetime.datetime.now().year,
            'archiv_name':datetime.datetime.utcnow().strftime("%Y.%m.%d_2_chast.rar"),
            'date_folder_name':datetime.datetime.utcnow().strftime("%d.%m.%Y_2_chast")
        }
        os.system(make_rar)