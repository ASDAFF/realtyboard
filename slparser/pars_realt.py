# -*- coding: utf-8 -*-
import csv, datetime, hashlib, json, os, pytz, random, re, urllib
from django.core.files.base import ContentFile
from grab.spider import Spider, Task
from grab import Grab
from grab.error import GrabNetworkError
from django.utils import timezone
from time import sleep
from board.models import Advert, City, Photo, SublocalityDetect,\
    ExtraCommercial, ExtraFlat, ExtraHouse, ExtraLot, ExtraRent,\
    BigSublocality, MetroDetect
from personal.models import UserData
from realtyboard.settings import USD_UAH, MEDIA_ROOT, PROXY_CREDENTIALS
from slparser.domria_metro import SUB_AVIS

import logging
logging.basicConfig(level=logging.DEBUG)

RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

DOMEN = 'http://realt.ua'

REGION = {'kharkov':'22',
         'kiev': '10'}


CATEGORIES= {'http://realt.ua/Db2/0Pr_Kv.php?Obl=%s&showNum=30' : 11,
             'http://realt.ua/Db2/0Pr_Dm.php?Obl=%s&showNum=30' : 14,
             'http://realt.ua/Db2/0Pr_Zm.php?Obl=%s&showNum=30' : 16,
             'http://realt.ua/Db2/0Sd_Kv.php?Obl=%s&tmSdD=9&showNum=30' : 21,
             'http://realt.ua/Db2/0Sd_Dm.php?Obl=%s&showNum=30' : 24,}





class RealtSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    # lexxx id 8606
    author_id = 8606
    stats = {'processed': 0, 'taken': 0, 'omited': 0,
             'without_phone': 0, 'saved': 0, 'date_of_update' : 0}

    def __init__(self, *args, **kwargs):
        self.city = kwargs.pop('city')
        self.city_id = City.objects.only('id').get(slug=self.city).id
        self.sublocality_marker = SublocalityDetect.objects.filter(city_id=self.city_id)
        self.metro_marker = MetroDetect.objects.filter(city_id=self.city_id)
        self.start_time = datetime.datetime.now()
        self.depth = datetime.timedelta(minutes=int(kwargs.pop('depth', 30)))
        self.stop_time = self.start_time - self.depth
        self.proxy_credentials = PROXY_CREDENTIALS['fine']
        super(RealtSpider, self).__init__(*args, **kwargs)

    def prepare(self):
        try:
            f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
            self.proxy_list = f.readlines()
        finally:
            f.close()

    def create_grab_instance(self, **kwargs):
        g = super(RealtSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = category %(REGION[self.city])
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)

    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        for i in grab.doc.select('//a[@class="avstd"]/@href'):
            one.append(i.text())
        for one_adv in one: 
            sleep(0.5)
            self.stats['processed'] += 1
            addition = task.get('addition')
            g = Grab()
            g.go(one_adv)
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = one_adv
            advert.title = g.doc.select('//h1').text()[:90]
            text = []
            for i in g.doc.select('//td[@colspan="2"]'):
                text.append(i.text())
            for i, img in enumerate(text):
                if u'Дополнительно : ' in img:
                    advert.main_text = re.sub(u'Дополнительно : ','',text[i]) 
            advert.sublocality_id = advert.detect_sublocality_id(self.sublocality_marker)
            advert.metro_id = advert.detect_metro_id(self.metro_marker)
            prise = g.doc.select('//font[@size="3"]/b').text()
            price_uah = re.sub(r' ','', prise)
            advert.price_uah = int(price_uah)
            mayn = []
            for i in g.doc.select('//table[@border="0"][@cellpadding="2"][@cellspacing="0"][@align="center"][@width="100%"]/tr'):
                mayn.append(i.text())
            phone = re.findall(u'Teлефоны : \d+\-\d+\-\d+', ''.join(mayn))
            phone2 = re.findall(u'Teлефон : \d+\-\d+\-\d+', ''.join(mayn))
            phone3 = re.findall(u'Teлефоны : \d+\-\d+\, \d+\-\d+\-\d+', ''.join(mayn))
            if phone:
                advert.raw_phones = ''.join(re.findall(r'\d+',''.join(phone)))
            if phone2:
                advert.raw_phones = ''.join(re.findall(r'\d+',''.join(phone2)))
            if phone3:
                phones = re.sub(r'\s|-','',''.join(phone3))
                advert.raw_phones = ''.join(re.findall(r'\d{8,12}',phones))
            objects = []
            for i in g.doc.select('//table[@border="0"][@cellpadding="5"][@cellspacing="0"][@width="100%"]'):
                objects.append(i.text())
            if CATEGORIES[addition['category']] in [11, 21]:
                extra_object = ExtraFlat()
                for i, img in enumerate(objects):
                    if u'Комнат / тип: ' in img:
                        rooms_number = re.findall(u'Комнат / тип: \d+', objects[i])
                        extra_object.rooms_number = ''.join(re.findall(r'\d+',''.join(rooms_number)))
                    if u'Этаж/этажность: ' in img:
                        floor = re.findall(u'Этаж/этажность: \d+', objects[i])
                        extra_object.floor = ''.join(re.findall(r'\d+',''.join(floor)))
                    if u' общая' in img:
                        total_area = re.findall(u'\d+ \- общая', objects[i])
                        extra_object.total_area = ''.join(re.findall(r'\d+',''.join(total_area)))
            if CATEGORIES[addition['category']] in [14,24]:
                extra_object = ExtraHouse()
                for i, img in enumerate(objects):
                    if u' общая' in img:
                        total_area = re.findall(u'\d+ \- общая', objects[i])
                        extra_object.total_area = ''.join(re.findall(r'\d+',''.join(total_area)))
                    if u'Этажность ' in img:
                        floor = re.findall(u'Этажность \d+', objects[i])
                        extra_object.floor = ''.join(re.findall(r'\d+',''.join(floor)))
            if CATEGORIES[addition['category']] in [16]:
                extra_object = ExtraLot()
                for i, img in enumerate(objects):
                    if u'Площадь : ' in img:
                        total_area = re.findall(u'Площадь : \d+', objects[i])
                        extra_object.total_area = ''.join(re.findall(r'\d+',''.join(total_area)))
            sleep(0.5)
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
            img = []
            for i in g.doc.select('//td[@class="tBrd1p"][@align="center"][@valign="middle"]/a/img/@src'):
                img.append(re.sub(r'\?t=\S+','',i.text()))
            for photo in img:
                q = Grab()
                photo_link = '%s%s' % (DOMEN, photo)
                photos = []
                photo_links2 = []
                sleep(0.2)
                try:
                    q.go(photo_link)
                    if q.response.code == 200 and \
                            re.match('image/', q.response.headers['Content-Type']):
                        photos.append({
                            'body': q.response.body,
                            'extention': RE_EXTENTION.search(q.config['url']).group()
                        })
                except GrabNetworkError as error:
                    photo_links2.append(photo)
                photo = Photo(advert_id=advert.id)
                file_name = '%s.%s' % (
                    hashlib.md5(q.config['url']).hexdigest(),
                    photos[0]['extention']
                    )
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
            if extra_object:
                extra_object.advert = advert
                extra_object.save()
            self.stats['saved'] += 1




