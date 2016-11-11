# -*- coding: utf-8 -*-
import csv, datetime, hashlib, json, os, pytz, random, re, urllib
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
from slparser.domria_metro import METRO_CIUA, SUB_CIUA

import logging
logging.basicConfig(level=logging.DEBUG)

URLS = {
    #Киев вся недвижимость за час (лимит 100)
    8: 'https://dom.ria.com/searchEngine/?page=0&limit=100&from_realty_id=&to_realty_id=&sort=0&category=0&realty_type=0&operation_type=0&state_id=10&city_id[15]=10&realty_id_only=&with_phone=&date_from=&date_to=&email=&period=per_hour&sortByLevels=1',
    #Харьков вся недвижимость за час (лимит 100)
    20: 'https://dom.ria.com/searchEngine/?page=0&limit=10&from_realty_id=&to_realty_id=&sort=0&category=0&realty_type=0&operation_type=0&state_id=7&city_id[25]=7&realty_id_only=&with_phone=&date_from=&date_to=&email=&period=per_hour&sortByLevels=1'
}   
URLS_ID = 'https://dom.ria.com/ru/realtor-%s.html'  #для телефона
PHOTO_URL = 'https://cdn.riastatic.com/photos/%s' #сылка на фото 
LINK_DOM = 'https://dom.ria.com/ru/%s' #сылка на обьявление на дом рии
RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

CATEGORIES= {'arenda-kvartir': 21,
             'arenda-domov': 24,
             'prodazha-kvartir': 11,
             'prodazha-domov': 14,}


class DomriaSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    author_id = 8606
    stats = {'processed': 0, 'taken': 0,'saved': 0}

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
        super(DomriaSpider, self).__init__(*args, **kwargs)

    def prepare(self):
        try:
            f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
            self.proxy_list = f.readlines()
        finally:
            f.close()

    def create_grab_instance(self, **kwargs):
        g = super(DomriaSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        url = URLS[self.city_id]
        yield Task('get_adverts',url)

    def task_get_adverts(self, grab, task):
        response = json.loads(grab.response.body)
        adv_list = response['items']
        adv_count = int(response['count'])
        for adv in adv_list:
            if adv['realty_type_name'] in [u'квартира',u'дом',u'Квартира',u'Дом']:
                if 'photos' in adv:
                    self.create_advert(adv)
        print(response['count'])

    def create_advert(self, raw):
        grab = Grab()
        self.stats['taken'] += 1
        self.stats['processed'] += 1
        # general fields
        extra_object = None
        adv = Advert()
        adv.city_id = self.city_id
        adv.author_id = self.author_id
        if 'priceArr' in raw:
            if raw['priceArr']['3']:
                price = re.sub(r'\s','',raw['priceArr']['3'])
                adv.price_uah = int(price)
            else:
                adv.price_uah = 1
        if 'description' in raw:
            adv.main_text = raw['description']
        if 'user' in raw:
            adv.contact_name = raw['user']['name']
        if 'user_id' in raw:
            us_id = raw['user_id']
            p = Grab()
            p.go(URLS_ID %us_id)
            main = p.doc.select("//li[@class='fieldWrap']").text()
            adv.raw_phones = re.sub(r'\s|\(|\)|\-', '', main)
        if 'street_name' in raw:
            adv.street = raw['street_name']
        if 'beautiful_url' in raw:
            url_domria = raw['beautiful_url']
            adv.link = (LINK_DOM %url_domria)
        if raw['advert_type_id'] in [1]:
            if raw['realty_type_name'] in [u'квартира', u'Квартира']:
                extra_object = ExtraFlat()
                adv.category_id = CATEGORIES['prodazha-kvartir']
                titles = u'Продажа квартиры %s'
                if 'floors_count' in raw:
                    extra_object.floors = raw['floors_count']
                if 'floor' in raw:
                    extra_object.floor = raw['floor']
                if 'rooms_count' in raw:
                    extra_object.rooms_number = raw['rooms_count']
                if 'total_square_meters' in raw:
                    extra_object.total_area = raw['total_square_meters']
            if raw['realty_type_name'] in [u'дом', u'Дом']:
                extra_object = ExtraHouse()
                adv.category_id = CATEGORIES['prodazha-domov']
                titles = u'Продажа дома %s'
                if 'total_square_meters' in raw:
                    extra_object.total_area = raw['total_square_meters']
        if raw['advert_type_id'] in [3,4]:
            if raw['realty_type_name'] in [u'квартира', u'Квартира']:
                extra_object = ExtraFlat()
                adv.category_id = CATEGORIES['arenda-kvartir']
                titles = u'Аренда квартиры %s'
                if 'floors_count' in raw:
                    extra_object.floors = raw['floors_count']
                if 'floor' in raw:
                    extra_object.floor = raw['floor']
                if 'rooms_count' in raw:
                    extra_object.rooms_number = raw['rooms_count']
                if 'total_square_meters' in raw:
                    extra_object.total_area = raw['total_square_meters']
            if raw['realty_type_name'] in [u'дом', u'Дом']:
                extra_object = ExtraHouse()
                adv.category_id = CATEGORIES['arenda-domov']
                titles = u'Аренда дома %s'
                if 'total_square_meters' in raw:
                    extra_object.total_area = raw['total_square_meters']
        if 'district_name' in raw:
            sudlo_name = int(SUB_CIUA[raw['district_name']]) 
            adv.sublocality_id = sudlo_name
            adv.title = (titles %adv.sublocality.name)
        if 'district_name' not in raw:
            if 'street_name' in raw:
                adv.title = (titles %raw['street_name'])
            else:
                adv.title = (titles %self.city)
        if self.metro_marker:
            if 'metro_station_name' in raw:
                metro_station = METRO_CIUA[raw['metro_station_name']]
                adv.metro_id = metro_station
        adv.save()
        photo_grab = grab.clone()
        photo_grab.setup(proxy_auto_change=False,
            reuse_referer=False)
        for key in raw['photos']:
            key_photo = raw['photos'][key]['file']
            photo_link = (PHOTO_URL %(key_photo.replace('.', 'f.')))
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
            photo = Photo(advert_id=adv.id)
            try:
                file_name = '%s.%s' % (
                        hashlib.md5(photo_grab.config['url']).hexdigest(),
                        photos[0]['extention']
                    )
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
            except IndexError:
                pass
        if extra_object:
            extra_object.advert = adv
            extra_object.save()
        self.stats['saved'] += 1









