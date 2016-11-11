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

DOMEN = 'http://md.mirkvartir.ua'

REGION = {'kharkov':'12346',
         'kiev': '5250'}

CATEGORIES= {'http://md.mirkvartir.ua/offers/?&type=dm&geo=city&gid=%s': 14,
             'http://md.mirkvartir.ua/offers/?&type=zm&geo=city&gid=%s': 24,
             }


class MirdmSpider(Spider):
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
        super(MirdmSpider, self).__init__(*args, **kwargs)

    # def prepare(self):
    #     try:
    #         f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
    #         self.proxy_list = f.readlines()
    #     finally:
    #         f.close()

    def create_grab_instance(self, **kwargs):
        g = super(MirdmSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = category % REGION[self.city]
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)

    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        for i in grab.doc.select('//@href'): 
            one.append(i.text())
            e = re.findall(r'/offers/\d+', ''.join(one))[::3]
        for one_adv in e: 
            extra_object = ExtraHouse()
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
            if g.doc.select('//div[@class="col-xs-6 col-md-5"]').text():
                phone = g.doc.select('//div[@class="col-xs-6 col-md-5"]').text()
                advert.raw_phones = '0'+''.join(re.findall(r'\d+', phone))
            if g.doc.select('//div[@class="col-xs-12 col-md-8"]').text():
                prise = g.doc.select('//div[@class="col-xs-12 col-md-8"]').text()
                advert.price_uah = int(''.join(re.findall(r'\d+', prise)))

            """
            Продолжить тут
            """
            
            text = g.doc.select('//td[@valign="top"][@width="100%"]').text()
            text = text.replace(advert.title, '')
            her = text.replace(advert.main_text, '')
            try:
                extra_object.total_area =re.search(r'\d+', re.search(u'Площадь дома\s+\-\s+\d+',her).group()).group()
            except AttributeError:
                a = 1
            try:
                extra_object.lot_area =re.search(r'\d+', re.search(u'Площадь участка\s+\-\s+\d+',her).group()).group()
            except AttributeError:
                a = 1
            try:
                extra_object.floors =re.search(r'\d+', re.search(u'Этажей\s+\-\s+\d+',her).group()).group()
            except AttributeError:
                a = 1
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
            for i in g.doc.select('//div[@class="thumb"]/a/@href'):
                img.append(i.text())
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

