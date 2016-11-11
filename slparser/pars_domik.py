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
from slparser.domria_metro import METRO_CIUA, SUB_CIUA

import logging
logging.basicConfig(level=logging.DEBUG)

DOMEN = {'kharkov': 'http://domik.ua/nedvizhimost/kharkov',
         'kiev': 'http://domik.ua/nedvizhimost/kiev'}

RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

CATEGORIES = {'snyat-kvartiru.html': 21,
              'snyat-kvartiru.html?page=15': 21,
              'snyat-kvartiru.html?page=30': 21,
              'arenda-kvartir-posutochno.html': 21,
              'arenda-v-novostrojkax.html': 21,
              'arenda-elitnyx-kvartir.html': 21,
              'arenda-domov.html': 24,
              'snyat-dom-posutochno.html': 24,
              'arenda-uchastkov.html':26,
              'arenda-kommercheskoj.html': 27,
              'kupit-kvartiry.html': 11,
              'kupit-kvartiry.html?page=15': 11,
              'kupit-kvartiry.html?page=30': 11,
              'prodazha-v-novostrojkax.html': 11,
              'prodazha-elitnyx-kvartir.html': 11,
              'prodazha-domov.html': 14,
              'prodazha-uchastkov.html': 16,
              'prodazha-kommercheskoj.html': 17}

class DomikSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    # lexxx id 8606
    author_id = 8606
    stats = {'processed': 0, 'taken': 0, 'omited': 0,
             'without_phone': 0, 'saved': 0, 'date_of_update': 0}

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
        super(DomikSpider, self).__init__(*args, **kwargs)

    # def prepare(self):
    #     try:
    #         f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
    #         self.proxy_list = f.readlines()
    #     finally:
    #         f.close()

    def create_grab_instance(self, **kwargs):
        g = super(DomikSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            url = '%s/%s' % (DOMEN[self.city], category)
            addition = {'category': category}
            yield Task('collect_adv_data', url, addition=addition)
            
    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        url_adv = []
        for i in grab.doc.select('//@href'):
            one.append(i.text())
        for item in one:
            if DOMEN[self.city][29:] == 'kharkov':
                if item.startswith('/nedvizhimost/xarkov-'):
                    url_adv.append(item)
                else:
                    continue
            else:
                if item.startswith('/nedvizhimost/%s-' % DOMEN[self.city][29:]):
                    url_adv.append(item)
                else:
                    continue
        for one_adv in url_adv:
            self.stats['processed'] += 1
            addition = task.get('addition')
            g = Grab()
            g.go(DOMEN[self.city][:15]+one_adv)
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = DOMEN[self.city][:15] + one_adv

            categories = g.doc.select('//div[@id="content_objectTabWidgetinfo_tab"]').text()

            if g.doc.select('//h1').text():
                title = g.doc.select('//h1').text()
                advert.title = title
            if g.doc.select('//p[@itemprop="average"]').text():
                numlist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                price = ""
                for i in g.doc.select('//p[@itemprop="average"]').text():
                    if i in numlist:
                        price += i
                advert.price_uah = int(price)
            if g.doc.select('//div[@class="objava_define"]').text():
                text = g.doc.select('//div[@class="objava_define"]').text()
                advert.main_text = text
            if g.doc.select('//p[@class="tel_user_obj tel"]').text():
                phones = g.doc.select('//p[@class="tel_user_obj tel"]').text()
                advert.raw_phones = phones
            if g.doc.select('//a[@class="ceeboxAuto"]').text():
                contact = g.doc.select('//a[@class="ceeboxAuto"]').text()
                advert.contact_name = contact
            if advert.category_id in [21,11,24,27,17]:
                extra_object = ExtraFlat()
                if u"Этаж" in categories:
                    separator1 = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Этаж').text().find(":")
                    both = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Этаж').text()[separator1 + 2:]
                    separator2 = both.find("/")
                    floors = both[separator2 + 1:]
                    floor = both[:separator2]
                    extra_object.floors = floors
                    extra_object.floor = floor
                if u"Комнат" in categories:
                    separator = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Комнат').text().find(":")
                    rooms_number = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Комнат').text()[separator + 2:separator + 3]
                    extra_object.rooms_number = rooms_number
                if u"Общая" in categories:
                    separator1 = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Общая').text().find(":")
                    full_area = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Общая').text()[separator1 + 2:]
                    separator2 = full_area.find(" ")
                    area = full_area[:separator2]
                    extra_object.total_area = area
            if advert.category_id in [14]:
                extra_object = ExtraHouse()
                if u"Этажей" in categories:
                    floors = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Этажей').text()[8:]
                    extra_object.floors = floors
                if u"Общая" in categories:
                    separator1 = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Общая').text().find(":")
                    full_area = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Общая').text()[separator1 + 2:]
                    separator2 = full_area.find(" ")
                    area = full_area[:separator2]
                    extra_object.total_area = area
            if advert.category_id in [16,26]:
                extra_object = ExtraLot()
                if u"Площадь" in categories:
                    separator1 = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Площадь').text().find(":")
                    area = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Площадь').text()[separator1 + 2:]
                    extra_object.total_area = area
                if u"Под ком. заст." or u"Под жил. заст." in categories:
                    granted = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" % u'Под').text()
                    extra_object.intended_purpose = granted
            if u"Метро" in categories:
                separator = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" % u'Метро').text().find("-")
                metro = g.doc.select("//div[@class='kratkost']/p[contains(.,'%s')]" %u'Метро').text()[7:separator - 2]
                if metro == u'Дворец Спорта':
                    advert.metro_id = 76
                elif metro == u'Дружбы Народов':
                    advert.metro_id = 79
                elif metro == u'Красный Хутор':
                    advert.metro_id = 87
                elif metro == u'Демеевская':
                    advert.metro_id = 66
                elif metro == u'Советской армии':
                    advert.metro_id = 21
                elif metro == u'Маршала Жукова':
                    advert.metro_id = 12
                elif metro == u'Метростроителей им. Ващенко':
                    advert.metro_id = 13
                elif metro == u'им. А.С. Масельского':
                    advert.metro_id = 9
                else:
                    advert.metro_id  = METRO_CIUA[metro]
            if g.doc.select("//div[@class='kratkost']").text():
                if DOMEN[self.city][29:] == 'kharkov':
                    separator1 = g.doc.select("//div[@class='kratkost']").text().find(",")
                    fulladress = g.doc.select("//div[@class='kratkost']").text()[separator1 + 11:]
                    separator2 = fulladress.find(",")
                    subloc = fulladress[:separator2]
                else:
                    separator1 = g.doc.select("//div[@class='kratkost']").text().find(",")
                    fulladress = g.doc.select("//div[@class='kratkost']").text()[separator1 + 2:]
                    separator2 = fulladress.find(",")
                    subloc = fulladress[:separator2]
                advert.sublocality_id = SUB_CIUA[subloc]
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
            for i in g.doc.select('//@href'):
                if i.text().startswith("/pic/objects/"):
                    img.append(i.text())
                else: continue
            for photo in img:
                photo_name_except = photo[22:54]
                photo_link = '%s%s' % (DOMEN[self.city][:15], photo)
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
                    file_name = file_name = '%s.%s' % (
                        hashlib.md5(photo_name_except).hexdigest(),
                        photos[0]['extention']
                    )
                photo.photo.save(file_name, ContentFile(photos[0]['body']))
            if extra_object:
                extra_object.advert = advert
                extra_object.save()
            self.stats['saved'] += 1