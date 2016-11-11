# -*- coding: utf-8 -*-
from board.models import *
from board.utils import parse_int, sort_phone
#from django.contrib.auth.models import User
from importdb.models import *
from personal.models import UserIP, UserData, UserOperation
from django.contrib.auth.models import Group
import re
import datetime
import sys
from board.my_import import big_sublocalities, sublocalities, metro

import logging
import os
count = 30

EXCLUDE_CAT = {15: 14, 25: 24, 35: 34, 45: 44, 13: 12, 23: 22, 33: 32, 43: 42, }


def groups():
    for rols in Roles.objects.all():
        Group.objects.get_or_create(id=rols.id, defaults={'name': rols.name})


def import_db_user():
    #global count

    Group.objects.all().delete()
    UserOperation.objects.all().delete()
    groups()

    for ui in Users.objects.all():  # [0:count]: #[0:30]
        ui.first_name = ui.first_name[:30].encode('utf-8')
        ui.username = ui.username[:30]
        print ui.id, ui.first_name

        user, c = UserData.objects.get_or_create(id=ui.id,
                                                 defaults={'username': ui.username,
                                                           'email': ui.email,
                                                           }
                                                 )
        if ui.for_django_import:
            user.set_password(ui.for_django_import)
        else:
            password = UserData.objects.make_random_password()
            user.set_password(password)

        user.first_name = ui.first_name
        user.remember = ui.for_django_import
        user.memoirs = ui.memoirs
        user.save()

        # us = UserData.objects.get(id=ui.id)
        us = UserData.objects.get(id=ui.id)

        try:
            ts = Bases.objects.get(user_id=ui.id)
            if ts:
                print ts.expiration
                day_last = ts.expiration - datetime.date.today()
                day_last = day_last - datetime.timedelta(days=1)
                if RolesUsers.objects.get(user_id=ui.id, role_id='5'):  # if is role 5 for add
                    us.set_ab_status(term=day_last.days)
        except Exception, ex:
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)  # выводит строку(номер) ошибки
            print ex

        if ui.ip:
            user_ip = UserIP.objects.get_or_create(ip=ui.ip)[0]
            user_ip.user.add(us)
            user_ip.save()

        sort_phone(ui.phone, us)


def import_db_city():
    for c in Cities.objects.all():
        city = City.objects.get_or_create(id=c.id)[0]
        city.id = c.id
        city.name = c.city
        city.slug = c.cityeng
        # exceptions for bad names
        if c.cityeng == u'lviv':
            city.slug = u'lvov'
        if c.cityeng == 'rowno':
            city.slug = 'rovno'
        if c.cityeng == 'ivano-Frankovsk':
            city.slug = 'ivano-frankovsk'
        city.save()


def import_db_category():
    for cat in Ncats.objects.all():
        category = Category.objects.get_or_create(id=cat.id)[0]
        if not cat.id in EXCLUDE_CAT:
            category.id = cat.id
            category.name = cat.cat
            category.save()


def import_db_metro():
    Metro.objects.all().delete()
    MetroLine.objects.all().delete()
    metro.import_data()


def import_region():
    BigSublocality.objects.all().delete()
    big_sublocalities.import_data()

    Sublocality.objects.all().delete()
    sublocalities.import_data()


def import_db_phones(phone):
    return phone


def import_db_ObjectType():
    for o in  Typeobjects.objects.all():
        objecttype = ObjectType()
        objecttype.id = o.id
        objecttype.name = o.typeobject
        objecttype.save()


def import_db(count=1000, citi=Kharkovs):
    # groups()
    # import_db_user()
    # import_db_city()
    # import_db_category() # this data created
    # import_region()
    # import_db_ObjectType()

    for ci in citi.objects.all()[0:count]:
        print citi
        # STRAT multy city
        if ci.cityeng == u'kharkov':
            try:
                advert = Advert.objects.get(id=ci.id)
            except Advert.DoesNotExist:
                advert = Advert()
                advert.id = ci.id
        elif ci.cityeng == u'kiev':
            try:
                advert = Advert.objects.get(id=ci.id+200000)
            except Advert.DoesNotExist:
                advert = Advert()

                advert.id = ci.id+200000
        else:
            try:
                advert = Advert.objects.get(id=ci.id+300000)
            except Advert.DoesNotExist:
                advert = Advert()
                advert.id = ci.id+300000
        # END multy city

        print ci.id, ci.cityeng, ci.cat_id,  # , ci.user_id

        try:
            advert.author = UserData.objects.get(id=ci.user_id)
        except UserData.DoesNotExist:
            pass
        advert.creation_date = ci.data
        advert.date_of_update = ci.data
        advert.main_text = ci.additionally
        #advert.non_admin_sublocality = ci.region_id

        if ci.currency and ci.currency == '1':
            advert.price_usd = parse_int(ci.cost)
        elif ci.currency and ci.currency == '2':
            advert.price_uah = parse_int(ci.cost)
        else:
            advert.price_uah = parse_int(ci.cost)

        advert.contact_name = ci.contact

    # foreign key-------------------------------------------------------------------------------------------------------
        try:
            metro = Metro.objects.get(id=ci.metro)
        except:
            metro = None
        advert.metro = metro

        try:
            city = City.objects.get(id=ci.city)
        except:
            city = None
        advert.city = city

        try:
            name_region = Kharkovregions.objects.get(id=ci.region_id)
            region = Sublocality.objects.get(name=name_region)
        except:
            region = None
        advert.sublocality = region


        if ci.cat_id in EXCLUDE_CAT:
            cat_id = EXCLUDE_CAT[ci.cat_id]
            cat_id = Category.objects.get(id=cat_id)
        else:
            if Category.objects.get(id=ci.cat_id) and ci.cat_id != 0:
                cat_id = Category.objects.get(id=ci.cat_id)

        advert.category = cat_id

        try:
            advert.save()
        except:
            pass
            # continue
    # extra key---------------------------------------------------------------------------------------------------------

        advert.extraflat = ExtraFlat(
            floor=ci.flor,
            floors=ci.allfloor,
            total_area=parse_int(ci.s),
            rooms_number=ci.komnat,
            condition=ci.state,
            )
        try:
            advert.extraflat.save()
        except Exception, ex:
            pass
            # print ex

        advert.extrahouse = ExtraHouse(
            floors=ci.allfloor,
            total_area=parse_int(ci.s),
            lot_area=ci.splant,
            condition=ci.state,
            gaz=not_empty(ci.gens),
            water=not_empty(ci.water),
            electricity=not_empty(ci.electro),
            )
        try:
            advert.extrahouse.save()
        except:
            pass

        advert.extralot = ExtraLot(
            lot_area=parse_int(ci.splant),
            gaz=not_empty(ci.gens),
            water=not_empty(ci.water),
            electricity=not_empty(ci.electro),
            )
        try:
            advert.extralot.save()
        except:
            pass

        advert.extrarent = ExtraRent(
            term=ci.period_rent,
            )
        try:
            advert.extrarent.save()
        except:
            pass

        advert.objecttype = ObjectType(
            name=ci.typeobject,
            )
        try:
            advert.ebjecttype.save()
        except:
            pass
        if ci.phone2:
            advert.raw_phones = ",".join([str(parse_int(ci.phone1)),
                                         str(parse_int(ci.phone2))])
        else:
            advert.raw_phones = ",".join([str(parse_int(ci.phone1)),])

        print 'phone = ', advert.raw_phones
#         for tel in phones:
#             if tel>0:
#                 owner = advert.author
#                 phone, c = Phone.objects.get_or_create(phone=tel,
#                                                     defaults={'owner':owner})
#                 print c
#
#                 advert.phones.add(phone)

        advert.save()
        #START make image
        # for (count, khimg) in enumerate(Kharkovimages.objects.filter(city_id=ci.id)):
        #     try:
        #         ph = "%s/%s" % (khimg.name[:2], khimg.name)
        #         Photo.objects.get_or_create(id=khimg.id, advert=advert, photo=ph)
        #     except Exception, ex:
        #         print ex
        #         print "Some else with images"
        # print 'count_image =', count

        send_image(citi, ci, advert)

        #END make image


def not_empty(value):
    if value:
        return 'есть'
    else:
        return ''


def find_phone_from_string(raw_tel):
    match = re.findall(r"/(?<!\w)(?:(?:(?:(?:\+?3)?8\W{0,5})?0\W{0,5})?[34569]\s?\d[^\w,;(\+]{0,5})?\d\W{0,5}\d\W{0,5}\d\W{0,5}\d\W{0,5}\d\W{0,5}\d\W{0,5}\d(?!(\W?\d))/x", raw_tel)
    return match


# def add_user_from_kohana(id_kohana_user):  # will dell this function after started project
#     user = UserData.objects.get(id=id_kohana_user)
#     created = User.objects.create(
#         id=user.id,
#         username=user.username,
#         email=user.email
#     )
#     if created:
#         created.set_password(user.for_django_import)
#         created.last_name = user.first_name[:30]


def send_image(citi, ci, advert):
    if ci.cityeng == u'kharkov':
        for (count, khimg) in enumerate(Kharkovimages.objects.filter(city_id=ci.id)):
            try:
                ph = "%s/%s" % (khimg.name[:2], khimg.name)
                Photo.objects.get_or_create(id=khimg.id, advert=advert, photo=ph)
            except Exception, ex:
                print ex
                print "Some else with images"
        # print 'count_image =', count
    elif ci.cityeng == u'kiev':
        for (count, khimg) in enumerate(Kievimages.objects.filter(city_id=ci.id)):
            try:
                ph = "%s/%s" % (khimg.name[:2], khimg.name)
                Photo.objects.get_or_create(id=khimg.id+200000, advert=advert, photo=ph)
            except Exception, ex:
                print ex
                print "Some else with images"
        # print 'count_image =', count
    else:
        for (count, khimg) in enumerate(Otherimages.objects.filter(city_id=ci.id)):
            try:
                ph = "%s/%s" % (khimg.name[:2], khimg.name)
                Photo.objects.get_or_create(id=khimg.id+300000, advert=advert, photo=ph)
            except Exception, ex:
                print ex
                print "Some else with images"
        # print 'count_image =', count
