# -*- coding: utf-8 -*-
import datetime
import hashlib
import os
import re
import urllib
import csv
import xml
import httplib
from time import sleep
from xml.dom.minidom import parse
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from time import time

from grab import Grab
from grab.error import GrabNetworkError


from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from slparser.domria_metro import SUB_CIUA
from realtyboard.settings import PROJECT_PATH, MEDIA_ROOT
from board.models import Advert, City, Photo, SublocalityDetect,\
    ExtraCommercial, ExtraFlat, ExtraHouse, ExtraLot, ExtraRent,\
    BigSublocality, MetroDetect, PaidAdvert, PaidService
from realtyboard.settings import TEMPLATE_DIRS


author_id =  15551
#helpagent ci.ua = 26449
#helpagent local = 15551
#author_id = 8606


term = 7

CIUA = "ci.ua%s"

RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

CATEGORIES = {'arenda-kvartir': 21,
             'arenda-domov': 24,
             'sdam-gostinku-komnatu': 22,
             'sdam-uchastok' : 26,
             'sdam-kommercheskuyu-nedvizhimost': 27,
             'prodazha-kvartir': 11,
             'prodazha-domov': 14,
             'prodam-gostinku-komnatu' : 12,
             'prodam-uchastok':16,
             'prodam-kommercheskuyu-nedvizhimost':17,
}       

# CITY = { u'АР Крым' : 1,
#          u'Винницкая' : 2,
#          u'Днепропетровская' : 3,
#          u'Донецкая' : 4,
#          u'Житомирская' : 5, 
#          u'Запорожская' : 6,
#          u'Ивано-Франковская' : 7,
#          u'Киевская' : 8,
#          u'Кировоградская' : 9,
#          u'Луганская' : 10,
#          u'Волынская' : 11, 
#          u'Львовская' : 12,
#          u'Николаевская' : 13,
#          u'Одесская' : 14,
#          u'Полтавская' : 15,
#          u'Ровно': 16,
#          u'Ровенская': 16,
#          u'Сумская' : 17, 
#          u'Тернопольская' : 18,
#          u'Закарпатская' : 19,
#          u'Харьковская' : 20,
#          u'Херсонская' : 21,
#          u'Хмельницкая' : 22,
#          u'Черкасская' : 23,
#          u'Черниговская' : 24,
#          u'Черновицкая' : 25,
# }

CITY = {
    u'Киев' :8,
}

stats = {'saved': 0, 'omited': 0}

def xml_save():
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/xml')
    # os.system('rm -r %s/*' % temp_dir) 
    # url = 'http://re.plektan.com/feeds/ebazar/kievrealty.xml'
    # html = urllib.urlopen(url).read()
    # f = open('%s/%s' % (temp_dir, 'helpagent.xml'),'w') 
    # f.write(html)
    # f.close()
    path = os.path.join(temp_dir, 'helpagent.xml')
    xml_import(path)

def xml_import(url):
    DOMTree = xml.dom.minidom.parse(url)
    collection = DOMTree.documentElement
    internal_adv = []
    link_adv = []
    g = Grab()
    u = []
    offers = collection.getElementsByTagName("offer")
    for offer in offers:
        u.append(offer)
        print offer.getAttribute("internal-id")
        advert = Advert()
        advert.author_id = author_id
        locations = offer.getElementsByTagName("location")
        for location in locations:
            # if location.getElementsByTagName('district'):
            #     advert.city_id = 8
            #     sublocality_marker = SublocalityDetect.objects.filter(city_id=8)
            #     metro_marker = MetroDetect.objects.filter(city_id=8)
            if location.getElementsByTagName('locality-name'):
                # region =  location.getElementsByTagName('locality-name')[0]
                # city = region.childNodes[0].data
                advert.city_id = 8
                sublocality_marker = SublocalityDetect.objects.filter(city_id=8)
                metro_marker = MetroDetect.objects.filter(city_id=8)
            if location.getElementsByTagName('address'):
                adress = location.getElementsByTagName('address')[0]
                advert.street = adress.childNodes[0].data
            if location.getElementsByTagName('longitude'):
                longitude = location.getElementsByTagName('longitude')[0]
                advert.longitude = longitude.childNodes[0].data
            if location.getElementsByTagName('latitude'):
                latitude = location.getElementsByTagName('latitude')[0]
                advert.latitude = latitude.childNodes[0].data
        agents = offer.getElementsByTagName("sales-agent")
        for agent in agents:
            if agent.getElementsByTagName('name'):
                name = agent.getElementsByTagName('name')[0]
                advert.contact_name = name.childNodes[0].data
            if agent.getElementsByTagName('phone'):
                phone = agent.getElementsByTagName('phone')[0]
                advert.raw_phones = phone.childNodes[0].data
        prices = offer.getElementsByTagName("price")
        for price in prices:
            if price.getElementsByTagName('currency'):
                currency =  price.getElementsByTagName('currency')[0]
                if currency.childNodes[0].data in ['UAH']:
                    price_uah = price.getElementsByTagName('value')[0]
                    advert.price_uah = float(price_uah.childNodes[0].data)
                if currency.childNodes[0].data in ['USD']:
                    price_usd = price.getElementsByTagName('value')[0]
                    advert.price_usd = float(price_usd.childNodes[0].data)
        types = offer.getElementsByTagName("type")
        categorys = offer.getElementsByTagName("category")
        for category in categorys:
            try:
                a = category.childNodes[0].data
            except IndexError:
                continue
            if category.childNodes[0].data in u'квартира' or u'офис':
                extra_object = ExtraFlat()
                for type in types:
                    if  type.childNodes[0].data in  u'продажа':
                        advert.category_id = CATEGORIES['prodazha-kvartir']
                        titles = u'Продажа квартиры %s'
                for type in types:
                    if  type.childNodes[0].data in  u'аренда':
                        advert.category_id = CATEGORIES['arenda-kvartir']
                        titles = u'Аренда квартиры %s'
                areas = offer.getElementsByTagName("area")
                for area in areas:
                    if area.getElementsByTagName('value'):
                        value = area.getElementsByTagName('value')[0]
                        extra_object.total_area = value.childNodes[0].data
                if offer.getElementsByTagName('floors-total'):
                    floors = offer.getElementsByTagName('floors-total')[0]
                    extra_object.floors = floors.childNodes[0].data
                if offer.getElementsByTagName('floor'):
                    floor = offer.getElementsByTagName('floor')[0]
                    extra_object.floor = floor.childNodes[0].data
                if offer.getElementsByTagName('rooms'):
                    rooms = offer.getElementsByTagName('rooms')[0]
                    extra_object.rooms_number = rooms.childNodes[0].data
            if category.childNodes[0].data in u'дом' or u'дача' or u'отдельные здания' or u'готовый бизнес' or 'коттедж' or u'объект сферы услуг':
                extra_object = ExtraHouse()
                for type in types:
                    if  type.childNodes[0].data in  u'продажа':
                        advert.category_id = CATEGORIES['prodazha-domov']
                        titles = u'Продажа дома %s'
                for type in types:
                    if  type.childNodes[0].data in  u'аренда':
                        advert.category_id = CATEGORIES['arenda-domov']
                        titles = u'Аренда дома %s'
                areas = offer.getElementsByTagName("area")
                for area in areas:
                    if area.getElementsByTagName('value'):
                        value = area.getElementsByTagName('value')[0]
                        extra_object.total_area = value.childNodes[0].data
            if category.childNodes[0].data in u'комната':
                extra_object = ExtraFlat()
                for type in types:
                    if  type.childNodes[0].data in  u'продажа':
                        advert.category_id = CATEGORIES['prodam-gostinku-komnatu']
                        titles = u'Продажа комнаты %s'
                for type in types:
                    if  type.childNodes[0].data in  u'аренда':
                        advert.category_id = CATEGORIES['sdam-gostinku-komnatu']
                        titles = u'Аренда комнаты %s'
                areas = offer.getElementsByTagName("area")
                for area in areas:
                    if area.getElementsByTagName('value'):
                        value = area.getElementsByTagName('value')[0]
                        extra_object.total_area = value.childNodes[0].data
                if offer.getElementsByTagName('floors-total'):
                    floors = offer.getElementsByTagName('floors-total')[0]
                    extra_object.floors = floors.childNodes[0].data
                if offer.getElementsByTagName('floor'):
                    floor = offer.getElementsByTagName('floor')[0]
                    extra_object.floor = floor.childNodes[0].data
                if offer.getElementsByTagName('rooms'):
                    rooms = offer.getElementsByTagName('rooms')[0]
                    extra_object.rooms_number = rooms.childNodes[0].data
            if category.childNodes[0].data in u'земельный участок' or u'таунхаус' or u'база отдыха, пансионат' :
                extra_object = ExtraLot()
                for type in types:
                    if  type.childNodes[0].data in  u'продажа':
                        advert.category_id = CATEGORIES['prodam-uchastok']
                        titles = u'Продажа участка %s'
                for type in types:
                    if  type.childNodes[0].data in  u'аренда':
                        advert.category_id = CATEGORIES['sdam-uchastok']
                        titles = u'Аренда участка %s'
                areas = offer.getElementsByTagName("lot-area")
                for area in areas:
                    if area.getElementsByTagName('value'):
                        value = area.getElementsByTagName('value')[0]
                        try:
                            extra_object.lot_area = value.childNodes[0].data
                        except IndexError:
                            extra_object.lot_area = 0
                    if area.getElementsByTagName('unit'):
                        unit = area.getElementsByTagName('unit')[0]
                        extra_object.lot_unit = unit.childNodes[0].data
                if offer.getElementsByTagName('lot-type'):
                    lot = offer.getElementsByTagName('lot-type')[0]
                    extra_object.intended_purpose = lot.childNodes[0].data
            if category.childNodes[0].data in u'производственные помещения' or u'торговые площади' or u'кафе, бар, ресторан' or u'помещения свободного назначения':
                extra_object = ExtraLot()
                for type in types:
                    if  type.childNodes[0].data in  u'продажа':
                        advert.category_id = CATEGORIES['prodam-kommercheskuyu-nedvizhimost']
                        titles = u'Продажа помещения %s'
                for type in types:
                    if  type.childNodes[0].data in  u'аренда':
                        advert.category_id = CATEGORIES['sdam-kommercheskuyu-nedvizhimost']
                        titles = u'Аренда помещения %s'
                areas = offer.getElementsByTagName("area")
                for area in areas:
                    if area.getElementsByTagName('value'):
                        value = area.getElementsByTagName('value')[0]
                        extra_object.lot_area = value.childNodes[0].data
                    if area.getElementsByTagName('unit'):
                        unit = area.getElementsByTagName('unit')[0]
                        extra_object.lot_unit = unit.childNodes[0].data
                if offer.getElementsByTagName('lot-type'):
                    lot = offer.getElementsByTagName('lot-type')[0]
                    extra_object.intended_purpose = lot.childNodes[0].data
        if offer.getElementsByTagName("description"):
            description = offer.getElementsByTagName("description")[0]
            advert.main_text = description.childNodes[0].data
        advert.title = (titles %advert.street)
        advert.sublocality_id = advert.detect_sublocality_id(sublocality_marker)
        advert.metro_id = advert.detect_metro_id(metro_marker)
        same_adv = Advert.objects.filter(main_text=advert.main_text).first()
        if same_adv:
            stats['omited'] += 1
            link_adv.append((CIUA  %same_adv.get_absolute_url()))
            internal_adv.append(offer.getAttribute("internal-id"))
            continue
        advert.save()
        # if offer.getElementsByTagName("fishka"):
        #     fishka = offer.getElementsByTagName('fishka')[0]
        #     if fishka.childNodes[0].data in 'videlennoe':
        #         service = PaidService.objects.get(name='adv_highlight')
        #         adv = Advert.objects.get(id=advert.id)
        #         user_operation = adv.activate_service(service=service, term=term,
        #                                                      info=u"helpagent")
        #     if fishka.childNodes[0].data in 'vip':
        #         service = PaidService.objects.get(name='adv_vip')
        #         adv = Advert.objects.get(id=advert.id)
        #         user_operation = adv.activate_service(service=service, term=term,
        #                                                      info=u"helpagent")
        #     if fishka.childNodes[0].data in 'top':
        #         service = PaidService.objects.get(name='adv_top')
        #         adv = Advert.objects.get(id=advert.id)
        #         user_operation = adv.activate_service(service=service, term=term,
        #                                                      info=u"helpagent")
        #     if fishka.childNodes[0].data in 'avtopodnatie':
        #         service = PaidService.objects.get(name='adv_auto_up')
        #         adv = Advert.objects.get(id=advert.id)
        #         user_operation = adv.activate_service(service=service, term=term,
        #                                                      info=u"helpagent")
        if offer.getElementsByTagName("image"):
            image = offer.getElementsByTagName("image")
            photo_grab = g.clone()
            photo_grab.setup(proxy_auto_change=False,reuse_referer=False)
            img = []
            for i in image:
                img.append(i.childNodes[0].data)
            for photo in img:
                photo_name_except = re.search(r'\w{8}', photo)
                photo_link = photo 
                photos = []
                photo_links2 = []
                sleep(0.2)
                try:
                    photo_grab.go(photo_link)
                    if photo_grab.response.code == 200 and \
                            re.match('image/', photo_grab.response.headers['Content-Type']):
                        photos.append({
                            'body': photo_grab.response.body,
                            'extention': RE_EXTENTION.search(photo_grab.config['url']).group()
                        })
                except GrabNetworkError as error:
                    photo_links2.append(photo_link)
                photo = Photo(advert_id=advert.id)
                try:
                    file_name = '%s.%s' % (
                        hashlib.md5(photo_grab.config['url']).hexdigest(),
                        photos[0]['extention']
                    )
                except UnicodeEncodeError:
                    file_name = '%s.%s' % (
                        hashlib.md5(photo_name_except).hexdigest(),
                        photos[0]['extention']
                    )
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
        if extra_object:
            extra_object.advert = advert
            extra_object.save()
        stats['saved'] += 1
        link_adv.append((CIUA  %advert.get_absolute_url()))
        internal_adv.append(offer.getAttribute("internal-id"))
    xml_result(internal_adv, link_adv)
    print stats

def xml_result(internal_adv,link_adv):
    if internal_adv and link_adv:
        temp_dir = os.path.join(PROJECT_PATH)
        source_file = open(os.path.join(temp_dir ,'templates/report.xml'), 'w')
        generated_on = str(datetime.datetime.now())
        source_file.write('<pre>')
        source_file.write('<?xml version="1.0" encoding="UTF-8" ?>\r\n')
        source_file.write('<result>\r\n')
        source_file.write(' <date>')
        source_file.write(generated_on)
        source_file.write('</date>\r\n')
        source_file.write(' <added>\r\n')
        for i, id_adv in enumerate(internal_adv):
            source_file.write(' internal-id :')
            source_file.write(id_adv)
            source_file.write(' ')
            source_file.write(link_adv[i])
            source_file.write(' ')
            source_file.write('</url>\r\n')
        source_file.write(' </added>\r\n')
        source_file.write('</result>\r\n')
        source_file.write('</pre>')
        source_file.close()



class Command(BaseCommand):

    def handle(self, *args, **options):
        o = xml_save()
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')

