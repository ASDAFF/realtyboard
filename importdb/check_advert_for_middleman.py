# -*- coding: utf-8 -*-
from importdb.models import Posredniks, Prorings
from board.models import Phone, Advert
from time import time
import datetime


# this start only one time
def check_advert_for_middleman():
    t1 = time()
    middleman = set([x['tel'] for x in Posredniks.objects.values('tel')])
    phones = Phone.objects.all()
    print 'total=', phones.count()
    for phone in phones:
        if phone.phone in middleman:
            print phone.phone
            phone.agent = 1
            try:
                phone.save()
            except Exception, ex:
                print ex
            for adv in phone.advert.all():
                print 'phone = ', phone.phone, 'id', adv.id
                adv.seller = 1
                adv.save()

    print("Total time %s" % (time() - t1))


# every time
def to_day_phone_of_rieltor():
    t1 = time()
    middleman = set([x['tel'] for x in Posredniks.objects.values('tel')])
    dt = datetime.datetime.today()
    #i = 0
    phones = Phone.objects.filter(date_of_addition__gte=dt)
    print 'total=', phones.count()
    #task.update_state(state='PROGRESS',
    #    meta={'current': i, 'total':phones.count()})
    for phone in phones:
    #    i+=1
    #    task.update_state(state='PROGRESS',
    #        meta={'current': i, 'total': Phone.objects.count()})
        if phone.phone in middleman:
            print phone.phone
            phone.agent = 1
            try:
                phone.save()
            except Exception, ex:
                print ex
            for adv in phone.advert.all():
                print 'phone = ', phone.phone, 'id', adv.id
                adv.seller = 1
                adv.save()

    print("Total time %s" % (time() - t1))
