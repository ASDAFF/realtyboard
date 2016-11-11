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


DOMEN = {'kharkov':'http://aviso.ua/kharkov/',
         'kiev': 'http://aviso.ua/kiev/'}

#&relevance=1 = за последний день
#&photo=1 - только где есть фото

CATEGORIES= {'list.php?r=101&relevance=1': 11,
             'list.php?r=106&relevance=1': 12,
             'list.php?r=121&relevance=1': 21,
             'list.php?r=126&relevance=1': 22,
             'list.php?r=131&relevance=1': 21,
             'list.php?r=136&relevance=1': 22,
             'list.php?r=191&relevance=1': 14,
             'list.php?r=196&relevance=1': 24,
             'list.php?r=192&relevance=1': 16,}


class AvisoSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    # lexxx id 8606
    author_id = 8606
    stats = {'processed': 0, 'taken': 0, 'omited': 0,
             'without_phone': 0, 'saved': 0, 'date_of_update' : 0}

    def __init__(self, *args, **kwargs):
        self.city = kwargs.pop('city')
        self.city_id = City.objects.only('id').get(slug=self.city).id
        if self.city_id == [20]:
            self.sublocality_marker = SublocalityDetect.objects.filter(
                city_id=20)
        if self.city_id in [20, 8, 3]:
            self.metro_marker = MetroDetect.objects.filter(
                city_id=self.city_id)
        self.start_time = datetime.datetime.now()
        self.depth = datetime.timedelta(minutes=int(kwargs.pop('depth', 30)))
        self.stop_time = self.start_time - self.depth
        self.proxy_credentials = PROXY_CREDENTIALS['fine']
        super(AvisoSpider, self).__init__(*args, **kwargs)

    # def prepare(self):
    #     try:
    #         f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
    #         self.proxy_list = f.readlines()
    #     finally:
    #         f.close()

    def create_grab_instance(self, **kwargs):
        g = super(AvisoSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = '%s%s' % (DOMEN[self.city], category)
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)

    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        for i in grab.doc.select('//@href'):
            one.append(i.text())
        print one
        print grab.response.url
        url_adv = re.findall(r'view\.\w+\?\w+\=\d+',','.join(one))
        for one_adv in url_adv:
            self.stats['processed'] += 1
            addition = task.get('addition')
            g = Grab()
            g.go(DOMEN[self.city]+one_adv)
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = re.sub(r'www.',"",DOMEN[self.city]+one_adv)
            if g.doc.select('//div[@class="page-header"]').text():
                title = g.doc.select('//div[@class="page-header"]').text()
                advert.title = title[:90]
            if g.doc.select('//p[@style="margin-top: 0;"]').text():
                text = g.doc.select('//p[@style="margin-top: 0;"]').text()
                advert.main_text = text
            adv = g.doc.select('//p[@class="phone"]').text()
            for i in SUB_AVIS:
                if i in adv:
                    advert.sublocality_id = SUB_AVIS[i]
            advert.metro_id = advert.detect_metro_id(self.metro_marker)
            if u'Цена:' in adv:
                if u'грн' in adv:
                    pr  = re.search(u'Цена: \d+\s+\d+', adv) or re.search(u'Цена: \d+', adv)
                    try:
                        room = re.sub(u'Цена: ',"",pr.group())
                        advert.price_uah = int(re.sub(' ',"", room))
                    except AttributeError:
                        advert.price_uah = 1
                if u'у.е.' in adv:
                    pr  = re.search(u'Цена: \d+\s+\d+', adv) or re.search(u'Цена: \d+', adv)
                    try:
                        room = re.sub(u'Цена: ',"",pr.group())
                        advert.price_usd = int(re.sub(' ',"", room))
                    except AttributeError:
                        advert.price_usd = 1
            if u'Тел:' in adv:
                phones = re.sub(r'[\s\-\(\)]', '', adv)
                phones = re.search(r'\d{9,10}(?=\D|$)', phones)
                advert.raw_phones = phones.group()
            if CATEGORIES[addition['category']] in [11, 12, 21, 22]:
                extra_object = ExtraFlat()
                if u'Комнат:' in adv:
                    lol  = re.search(u'Комнат: \d+', adv)
                    room = re.sub(u'Комнат: ',"",lol.group())
                    extra_object.rooms_number = int(room)
            if CATEGORIES[addition['category']] in [14, 24]:
                extra_object = ExtraHouse()
            if CATEGORIES[addition['category']] in [16]:
                extra_object = ExtraLot()
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
            for i in g.doc.select('//li[@class="span2"]/a[@class="thumbnail"]/@href'):
                img.append(i.text()[2:])
            for i in g.doc.select('//div[@class="item active"]/img/@src'):
                img.append(i.text()[2:])
            for photo in img:
                q = Grab()
                photos = []
                photo_links2 = []
                sleep(0.2)
                try:
                    q.go(photo)
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
            








