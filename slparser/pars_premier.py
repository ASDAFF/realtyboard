# -*- coding: utf-8 -*-
import csv, datetime, hashlib, json, os, pytz, random, re, urllib
from django.utils import timezone
from django.core.files.base import ContentFile
from grab.spider import Spider, Task
from grab import Grab
from grab.error import GrabNetworkError
from time import sleep
from board.models import Advert, City, Photo, SublocalityDetect,\
    ExtraCommercial, ExtraFlat, ExtraHouse, ExtraLot, ExtraRent,\
    BigSublocality, MetroDetect
from personal.models import UserData
from realtyboard.settings import USD_UAH, MEDIA_ROOT, PROXY_CREDENTIALS
from slparser.domria_metro import METRO_PREM, SUB_PREM

import logging
logging.basicConfig(level=logging.DEBUG)

DOMEN = "http://premier.ua/"
DOMEN2 =  "http://premier.ua"

RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

CATEGORIES = { '/subcategory-51-page-1.aspx' : 21 , #Аренда
               '/subcategory-51-page-2.aspx' : 21 ,
               '/subcategory-51-page-3.aspx' : 21 ,
               '/subcategory-51-page-4.aspx' : 21 ,
               '/subcategory-70-page-1.aspx' : 11, #Квартиры в новостройках
               '/subcategory-75-page-1.aspx' : 11,#Продажа мн-х, элитных 
               '/subcategory-80-page-1.aspx' : 11, #Продажа 1-комн.кв. 
               '/subcategory-100-page-1.aspx' : 11, #Продажа 2-комн.кв
               '/subcategory-120-page-1.aspx' : 11,#Продажа 3-комн.кв. 
               '/subcategory-140-page-1.aspx' : 11,#Продажа 4-комн.кв.
               '/subcategory-160-page-1.aspx' : 12, #Продажа гостинок, комнат 
               '/subcategory-165-page-1.aspx' : 16,#Участки в Харькове 
               '/subcategory-166-page-1.aspx' : 16,#Участки в пригороде 
               '/subcategory-167-page-1.aspx' : 16,#Участки в Харьковской области 
               '/subcategory-169-page-1.aspx' : 14,#Продажа домов в Харькове 
               '/subcategory-180-page-1.aspx' : 14,#Продажа домов в пригороде 
               '/subcategory-190-page-1.aspx' : 14, #Дома в Харьковской области
}

class PremierSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    # lexxx id 8606
    author_id = 8606
    stats = {'processed': 0, 'taken': 0, 'omited': 0,
             'without_phone': 0, 'saved': 0, 'date_of_update' : 0}

    def __init__(self, *args, **kwargs):
        self.city = kwargs.pop('city')
        self.city_id = City.objects.only('id').get(slug=self.city).id
        self.sublocality_marker = SublocalityDetect.objects.filter(
            city_id=self.city_id)
        self.metro_marker = MetroDetect.objects.filter(city_id=self.city_id)
        # depth should be set in minutes
        self.start_time = datetime.datetime.now()
        self.depth = datetime.timedelta(minutes=int(kwargs.pop('depth', 30)))
        self.stop_time = self.start_time - self.depth
        self.proxy_credentials = PROXY_CREDENTIALS['fine']
        # print '//////////stop time ', self.stop_time, '//////////////////'
        super(PremierSpider, self).__init__(*args, **kwargs)

    # def prepare(self):
    #     try:
    #         f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
    #         self.proxy_list = f.readlines()
    #     finally:
    #         f.close()

    def create_grab_instance(self, **kwargs):
        g = super(PremierSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = '%s%s' % (DOMEN, category) 
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)
            
    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        for i in grab.doc.select('//@href'):
            one.append(i.text())
        url_adv = re.findall(r'adv-\d+\.\w+', ','.join(one))[0::3]
        for one_adv in url_adv:
            self.stats['processed'] += 1
            addition = task.get('addition')
            g = Grab()
            g.go(DOMEN+one_adv)
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = DOMEN + one_adv
            categories = g.doc.select('//table[@class="adv_info_table"]').text()

            if g.doc.select('//h2[@class="pagetitle"]').text():
                title = g.doc.select('//h2[@class="pagetitle"]').text()
                advert.title = title
            price = g.doc.select('//td[@class="adv-price"]').text()
            if price:
                price_search = re.findall('\d+', price)
                price_one =""
                for i in price_search:
                    price_one +=i
                advert.price_uah = int(price_one) 
            else:
                advert.price_uah = 1
            if u"Описание:" in categories:
                text = g.doc.select('//td[@style="border-bottom:none;"][@colspan="2"]').text()
                if text:
                    advert.main_text = text
            if u"Телефон:" in categories:
                phones = re.sub(u'Телефон:',"",g.doc.select(
                    "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Телефон').text())
                if phones:
                    phon = re.sub(r'\-',"",phones)
                    advert.raw_phones = phon
            if u"Имя, фамилия:" in categories:
                contact = re.sub(u'Имя, фамилия:',"",g.doc.select(
                    "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Имя').text())
                if contact:
                    advert.contact_name = contact
            if advert.category_id in [21,11,12]:
                extra_object = ExtraFlat()
                if u"Этажность" in categories:
                    floors = re.sub(u'Этажность ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Этажность').text())
                    if floors:
                        extra_object.floors = floors
                if u"Этаж" in categories:
                    floor = re.sub(u'Этаж ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Этаж').text())
                    if floor:
                        extra_object.floor = floor
                if u"Количество комнат" in categories:
                    rooms_number = re.sub(u'Количество комнат ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Количество комнат').text())
                    if rooms_number:
                        extra_object.rooms_number = rooms_number
                if u"Общая площадь" in categories:
                    area = re.sub(u'Общая площадь ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Общая площадь').text())
                    area_search = re.search('\d+', area)
                    if area_search:
                        extra_object.total_area = area_search.group()
            if advert.category_id in [14]:
                extra_object = ExtraHouse()
                if u"Этажность" in categories:
                    floors = re.sub(u'Этажность ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Этажность').text())
                    if floors:
                        extra_object.floors = floors
                if u"Общая площадь" in categories:
                    area = re.sub(u'Общая площадь ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Общая площадь').text())
                    area_search = re.search('\d+', area)
                    if area_search:
                        extra_object.total_area = area_search.group()
            if advert.category_id in [16]:
                extra_object = ExtraLot()
                if u"Общая площадь" in categories:
                    area = re.sub(u'Общая площадь ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Общая площадь').text())
                    area_search = re.search('\d+', area)
                    if area_search:
                        extra_object.total_area = area_search.group()
            if self.metro_marker:
                metroc = advert.detect_metro_id(self.metro_marker)
                if metroc:
                    advert.metro_id = metroc
                if u"Метро" in categories:
                    metro = re.sub(u'Метро ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Метро').text())
                    if metro:
                        advert.metro_id  = METRO_PREM[metro]
            if self.sublocality_marker:
                subloc = advert.detect_sublocality_id(self.sublocality_marker)
                if subloc:
                    advert.sublocality_id = subloc
                if u"Район" in categories:
                    subloc = re.sub(u'Район ',"",g.doc.select(
                        "//table[@class='adv_info_table']/tr[contains(.,'%s')]" %u'Район').text())
                    if subloc:
                        advert.sublocality_id = SUB_PREM[subloc]
            same_adv = Advert.objects.filter(
                    category_id=CATEGORIES[addition['category']],
                    author_id=self.author_id,
                    city_id=self.city_id,
                    link=advert.link,
                ).first()
            if same_adv:
                self.stats['omited'] += 1
                if same_adv.date_of_update < (
                            timezone.now() - datetime.timedelta(hours=20)):
                        same_adv.date_of_update = timezone.now()
                        same_adv.save()
                        self.stats['date_of_update'] += 1
                continue
            advert.save()
            photo_grab = g.clone()
            photo_grab.setup(proxy_auto_change=False,reuse_referer=False)
            img = []
            for i in g.doc.select('//a[@data-lightbox="advertisement-images"]/@href'):
                img.append(i.text())
            for photo in img:
                photo_name_except = re.search(r'\d{8}', photo).group()
                photo_link = '%s%s' % (DOMEN2, photo)
                photos = []
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
                    file_name = file_name = '%s.%s' % (
                        hashlib.md5(photo_name_except).hexdigest(),
                        photos[0]['extention']
                    )
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
            if extra_object:
                extra_object.advert = advert
                extra_object.save()
            self.stats['saved'] += 1