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

DOMEN = 'http://mirkvartir.ua'

NUM = {'kharkov':'12346',
         'kiev': '5250'}

CATEGORIES= {'http://mirkvartir.ua/offers/list?oper=pr&type=kv&city=%s&colCom=1|2|3|4|5': 11,
             'http://mirkvartir.ua/offers/list?oper=pr&type=kv&city=%s&colCom=1|2|3|4|5&page=2': 11,
             'http://mirkvartir.ua/offers/list?oper=pr&type=kv&city=%s&colCom=1|2|3|4|5&page=3': 11,
             'http://mirkvartir.ua/offers/list?oper=pr&type=kv&city=%s&colCom=1|2|3|4|5&page=4': 11,
             'http://mirkvartir.ua/offers/list?oper=pr&type=kv&city=%s&colCom=1|2|3|4|5&page=5': 11,
             'http://mirkvartir.ua/offers/list?oper=pr&type=km&city=%s&colCom=1|2|3|4|5': 12,
             'http://mirkvartir.ua/offers/list?oper=ar&type=kv&city=%s&colCom=1|2|3|4|5': 21,
             'http://mirkvartir.ua/offers/list?oper=ar&type=km&city=%s&colCom=1|2|3|4|5': 22,
             }


class MirkvSpider(Spider):
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
        super(MirkvSpider, self).__init__(*args, **kwargs)

    def prepare(self):
        try:
            f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
            self.proxy_list = f.readlines()
        finally:
            f.close()

    def create_grab_instance(self, **kwargs):
        g = super(MirkvSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = category %(NUM[self.city])
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)

    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        for i in grab.doc.select('//a/@href'):
            one.append(i.text())
        url_adv = re.findall(r'/offers/view/\d+',','.join(one))[0::3]
        for one_adv in url_adv: 
            extra_object = ExtraFlat()
            in1 = []
            in2 = []
            self.stats['processed'] += 1
            addition = task.get('addition')
            g = Grab()
            g.go(DOMEN+one_adv)
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = DOMEN+one_adv
            if g.doc.select('//article[@class="article"]/h1').text():
                title = g.doc.select('//article[@class="article"]/h1').text()
                advert.title = title[:90]
            if g.doc.select('//div[@class="box"]/p').text():
                text = g.doc.select('//div[@class="box"]/p').text()
                advert.main_text = text
            advert.sublocality_id = advert.detect_sublocality_id(self.sublocality_marker)
            advert.metro_id = advert.detect_metro_id(self.metro_marker)
            for i in g.doc.select('//div[@class="col-xs-12 col-md-8"]'):
                in1.append(i.text())
                in1 = in1[:2]
            for i in g.doc.select('//div[@class="col-xs-12 col-md-7"]'):
                in2.append(i.text())
                in2 = in2[:3]
            if in1[0] is not '-':
                if u'грн.' in in1[0]:
                    price_uah = ''.join(re.findall(r'\d+', in1[0]))
                    advert.price_uah = int(price_uah)
                if '$' in in1[0]:
                    price_usd = ''.join(re.findall(r'\d+', in1[0]))
                    advert.price_usd = int(price_usd)
            if in1[1] is not '-':
                if self.city_id in [20]:
                    advert.street = re.sub(u'Харьковская обл., Харьков, ','',in1[1])
                if self.city_id in [8]:
                    advert.street = re.sub(u'Киев, ','',in1[1])
            one = g.doc.select('//div[@class="col-xs-6 col-md-5"]').text()
            two = g.doc.select('//a[@class="pseudo show_phone"]/@data-content').text()
            advert.raw_phones = ''.join(re.findall(r'\d+', one)) + ''.join(re.findall(r'\d+', two))
            ini = re.findall(r'\d+', ''.join(in2[0]))
            if ini:
                extra_object.rooms_number = ''.join(ini)
            ini = re.findall(r'\d+', ''.join(in2[1]))
            if ini:
                extra_object.floor = ''.join(ini[0])
                try:
                    extra_object.floors = ''.join(ini[1])
                except IndexError: 
                    extra_object.floors = ''.join(ini[0])
            ini = re.findall(r'\d+', re.sub(u'м2','',''.join(in2[2])))
            if ini:
                extra_object.total_area = ''.join(ini)
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
            for i in g.doc.select('//a[@href=""]/img/@src'):
                img.append(i.text())
            for photo in img:
                q = Grab()
                if u'aspo' in photo:
                    photo_link = photo
                else:
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
                try:
                    file_name = '%s.%s' % (
                        hashlib.md5(q.config['url']).hexdigest(),
                        photos[0]['extention']
                        )
                except IndexError:
                    continue
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
            if extra_object:
                extra_object.advert = advert
                extra_object.save()
            self.stats['saved'] += 1

