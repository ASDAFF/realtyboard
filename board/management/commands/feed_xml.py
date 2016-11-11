# -*- coding: utf-8 -*-
import os
import io
import datetime
from time import time

from xml.dom import minidom

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from slparser.domria_metro import SUB_CIUA
from realtyboard.settings import PROJECT_PATH, MEDIA_ROOT
from board.models import Advert, City, Photo, SublocalityDetect,\
    ExtraCommercial, ExtraFlat, ExtraHouse, ExtraLot, ExtraRent,\
    BigSublocality, MetroDetect
from slparser.domria_metro import FEED_PLECTAN, FEED_PLECTAN_METRO,FEED_PLECTAN_OBLAST,\
    FEED_PLECTAN_OBLAST_KH,FEED_PLECTAN_KIEV,FEED_PLECTAN_KIEV_DIST

TYPE = {
    'prodam-kvartiru': 'sell',
    'prodam-gostinku-komnatu':'sell',
    'prodam-dom':'sell',
    'prodam-uchastok':'sell',
    'prodam-kommercheskuyu-nedvizhimost':'sell',
    'sdam-kvartiru': 'rent_long',
    'sdam-gostinku-komnatu':'rent_long',
    'sdam-dom':'rent_long',
    'sdam-uchastok':'rent_long',
    'sdam-kommercheskuyu-nedvizhimost':'rent_long',
    'kuplyu-kvartiru': 'buy',
    'kuplyu-gostinku-komnatu': 'buy',
    'kuplyu-dom': 'buy',
    'kuplyu-uchastok': 'buy',
    'kuplyu-kommercheskaya-nedvizhimost': 'buy',
    'snimu-kvartiru': 'hire_long',
    'snimu-gostinku-komnatu': 'hire_long',
    'snimu-dom': 'hire_long',
    'snimu-uchastok': 'hire_long',
    'snimu-kommercheskuyu-nedvizhimost':'hire_long',

}

PROPERTY_TYPE = {
    'prodam-kvartiru': 'flat',
    'prodam-gostinku-komnatu':'flat',
    'prodam-dom':'house',
    'prodam-uchastok':'plot',
    'prodam-kommercheskuyu-nedvizhimost':'commercial',
    'sdam-kvartiru': 'flat',
    'sdam-gostinku-komnatu':'flat',
    'sdam-dom':'house',
    'sdam-uchastok':'plot',
    'sdam-kommercheskuyu-nedvizhimost':'commercial',
    'kuplyu-kvartiru': 'flat',
    'kuplyu-gostinku-komnatu': 'flat',
    'kuplyu-dom': 'house',
    'kuplyu-uchastok': 'plot',
    'kuplyu-kommercheskaya-nedvizhimost': 'commercial',
    'snimu-kvartiru': 'flat',
    'snimu-gostinku-komnatu': 'flat',
    'snimu-dom': 'house',
    'snimu-uchastok': 'plot',
    'snimu-kommercheskuyu-nedvizhimost':'commercial',
}

URL_PHOTO = 'http://ci.ua'

SLUG = 'http://ci.ua'

CITY = {
    'kiev' :8,
    'kharkov':20,
}

REGION = {
    'kiev' :u'Київська область',
    'kharkov':u'Харківська область',
}

LOC_NAME = {
    'kiev' :u'Київ',
    'kharkov':u'Харків',
}

year = datetime.date.today().year
month = datetime.date.today().month
day = datetime.date.today().day 

def adver_feed(city):
    time = datetime.datetime.now()
    now_time = time.strftime("%H:%M")
    past_time = "%s:%s"%(time.hour -1, time.minute)
    adverts = Advert.objects.filter(city_id=CITY[city],date_of_update__range=["%s-%s-%s %s" %(year,month,day,past_time),
                                                            "%s-%s-%s %s" %(year,month,day,now_time)])
    doc = minidom.Document()
    root = doc.createElement('realty-feed')
    doc.appendChild(root)
    generation = doc.createElement('generation-date')
    text = doc.createTextNode("%s-%s-%s %s" %(year,month,day,now_time))
    generation.appendChild(text)
    root.appendChild(generation)
    for adv in adverts:
        try:
            phone = adv.phone_set.all()[0]
        except IndexError:
            continue
        if phone.agent not in [1,2,3,5]:
            print adv.id
            offer = doc.createElement('offer')
            offer.setAttribute(' internal-id', '%s' %(adv.id))
            root.appendChild(offer)
            tipe  = doc.createElement('type')
            text = doc.createTextNode('%s'%(TYPE[adv.category.slug]))
            tipe.appendChild(text)
            offer.appendChild(tipe)
            property_type  = doc.createElement('property-type')
            text = doc.createTextNode('%s'%(PROPERTY_TYPE[adv.category.slug]))
            property_type.appendChild(text)
            offer.appendChild(property_type)
            url  = doc.createElement('url')
            text = doc.createTextNode('%s%s'%(SLUG, adv.get_absolute_url()))
            url.appendChild(text)
            offer.appendChild(url)
            creation_date  = doc.createElement('creation-date')
            new_time = "%s:%s"%(adv.date_of_update.hour +3, adv.date_of_update.minute)
            text = doc.createTextNode('%s-%s-%s %s'%(adv.date_of_update.year, adv.date_of_update.month,adv.date_of_update.day ,new_time))
            creation_date.appendChild(text)
            offer.appendChild(creation_date)
            location = doc.createElement('location')
            offer.appendChild(location)
            country  = doc.createElement('country')
            text = doc.createTextNode('Ukraine')
            country.appendChild(text)
            location.appendChild(country)
            region  = doc.createElement('region')
            text = doc.createTextNode(u'%s'%(REGION[city]))
            region.appendChild(text)
            location.appendChild(region)
            if CITY[city] is 8:
                if adv.sublocality:
                    if adv.sublocality.name in FEED_PLECTAN_KIEV_DIST:
                        locality_name  = doc.createElement('district')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN_KIEV_DIST[adv.sublocality.name]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
                    if adv.sublocality.name in FEED_PLECTAN_KIEV:
                        locality_name  = doc.createElement('locality-name')
                        text = doc.createTextNode(u'%s'%(LOC_NAME[city]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
                        sub_locality  = doc.createElement('non-admin-sub-locality')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN_KIEV[adv.sublocality.name]))
                        sub_locality.appendChild(text)
                        location.appendChild(sub_locality)
                if adv.big_sublocality:
                        locality_name  = doc.createElement('locality-name')
                        text = doc.createTextNode(u'%s'%(LOC_NAME[city]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
                        sub_locality  = doc.createElement('non-admin-sub-locality')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN_KIEV[adv.big_sublocality.name]))
                        sub_locality.appendChild(text)
                        location.appendChild(sub_locality)
            if CITY[city] is 20:
                if adv.sublocality:
                    if adv.sublocality.name in FEED_PLECTAN:
                        locality_name  = doc.createElement('locality-name')
                        text = doc.createTextNode('%s'%(LOC_NAME[city]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
                        sub_locality  = doc.createElement('non-admin-sub-locality')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN[adv.sublocality.name]))
                        sub_locality.appendChild(text)
                        location.appendChild(sub_locality)
                    if adv.sublocality.name in FEED_PLECTAN_OBLAST_KH:
                        locality_name  = doc.createElement('district')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN_OBLAST_KH[adv.sublocality.name]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
                    if adv.sublocality.name in FEED_PLECTAN_OBLAST:
                        locality_name  = doc.createElement('district')
                        text = doc.createTextNode(u'%s'%(FEED_PLECTAN_OBLAST[adv.sublocality.name]))
                        locality_name.appendChild(text)
                        location.appendChild(locality_name)
            if adv.category_id in [21, 11, 12, 22]:
                try:
                    if adv.extraflat.rooms_number:
                        rooms_number  = doc.createElement('rooms')
                        text = doc.createTextNode('%s'%(adv.extraflat.rooms_number))
                        rooms_number.appendChild(text)
                        offer.appendChild(rooms_number)
                    if adv.extraflat.floor:
                        floor  = doc.createElement('floor')
                        text = doc.createTextNode('%s'%(adv.extraflat.floor))
                        floor.appendChild(text)
                        offer.appendChild(floor)
                    if adv.extraflat.floors:
                        floors  = doc.createElement('floors-total')
                        text = doc.createTextNode('%s'%(adv.extraflat.floors))
                        floors.appendChild(text)
                        offer.appendChild(floors)
                    if adv.extraflat.total_area:
                        total_area = doc.createElement('area')
                        offer.appendChild(total_area)
                        value  = doc.createElement('value')
                        text = doc.createTextNode('%s'%(adv.extraflat.total_area))
                        value.appendChild(text)
                        total_area.appendChild(value)
                        unit  = doc.createElement('unit')
                        text = doc.createTextNode(u'кв.м')
                        unit.appendChild(text)
                        total_area.appendChild(unit)
                except ObjectDoesNotExist:
                    pass
            if adv.category_id in [14, 24]:
                try:
                    if adv.extrahouse.floors:
                        floors  = doc.createElement('floors')
                        text = doc.createTextNode('%s'%(adv.extrahouse.floors))
                        floors.appendChild(text)
                        offer.appendChild(floors)
                    if adv.extrahouse.total_area:
                        total_area = doc.createElement('area')
                        offer.appendChild(total_area)
                        value  = doc.createElement('value')
                        text = doc.createTextNode('%s'%(adv.extrahouse.total_area))
                        value.appendChild(text)
                        total_area.appendChild(value)
                        unit  = doc.createElement('unit')
                        text = doc.createTextNode(u'кв.м')
                        unit.appendChild(text)
                        total_area.appendChild(unit)
                except ObjectDoesNotExist:
                    pass
            if adv.category_id in [16, 17, 26, 27]:
                try:
                    if adv.extralot.lot_area:
                        total_area = doc.createElement('area')
                        offer.appendChild(total_area)
                        value  = doc.createElement('value')
                        text = doc.createTextNode('%s'%(adv.extralot.lot_area))
                        value.appendChild(text)
                        total_area.appendChild(value)
                        unit  = doc.createElement('unit')
                        text = doc.createTextNode(u'кв.м')
                        unit.appendChild(text)
                        total_area.appendChild(unit)
                except ObjectDoesNotExist:
                    pass
            price = doc.createElement('price')
            offer.appendChild(price)
            value  = doc.createElement('value')
            text = doc.createTextNode('%s'%(adv.price_uah))
            value.appendChild(text)
            price.appendChild(value)
            currency  = doc.createElement('currency')
            text = doc.createTextNode('UAH')
            currency.appendChild(text)
            price.appendChild(currency)
            sales_agent = doc.createElement('sales-agent')
            offer.appendChild(sales_agent)
            for i in adv.phone_set.all():
                phone  = doc.createElement('phone')
                text = doc.createTextNode('0%s'%(i))
                phone.appendChild(text)
                sales_agent.appendChild(phone)
            description  = doc.createElement('description')
            text = doc.createTextNode('%s'%(adv.main_text))
            description.appendChild(text)
            offer.appendChild(description)
            if adv.metro:
                metro  = doc.createElement('metro')
                text = doc.createTextNode(u'%s'%(FEED_PLECTAN_METRO[adv.metro.name]))
                metro.appendChild(text)
                offer.appendChild(metro)
            if adv.photo_set.all():
                for i in adv.photo_set.all():
                    image  = doc.createElement('image')
                    text = doc.createTextNode('%s%s'%(URL_PHOTO,i.photo.url))
                    image.appendChild(text)
                    offer.appendChild(image)

    temp_dir = os.path.join(PROJECT_PATH)
    file_path = os.path.join(temp_dir ,'templates/feed_ciua_kiev.xml')

    xml_str = doc.toprettyxml(indent="  ",encoding="UTF-8")
    temp_dir = os.path.join(PROJECT_PATH)
    f = open(os.path.join(temp_dir ,'templates/feed_ciua_%s.xml')%(city),'wt')
    f.write(xml_str)
    f.close()

class Command(BaseCommand):

    def handle(self, *args, **options):
        o = adver_feed(city=args[0])
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')
