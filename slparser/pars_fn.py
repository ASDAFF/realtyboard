# -*- coding: utf-8 -*-
import csv, datetime, hashlib, json, os, pytz, random, re, urllib
from django.utils import timezone
from django.core.files.base import ContentFile
from grab.spider import Spider, Task
from grab import Grab
from grab.error import GrabNetworkError, DataNotFound
from time import sleep
from board.models import Advert, City, Photo, SublocalityDetect,\
    ExtraCommercial, ExtraFlat, ExtraHouse, ExtraLot, ExtraRent,\
    BigSublocality, MetroDetect
from personal.models import UserData
from realtyboard.settings import USD_UAH, MEDIA_ROOT, PROXY_CREDENTIALS
from slparser.domria_metro import SUB_FN

import logging
logging.basicConfig(level=logging.DEBUG)

DOMEN = 'http://fn.ua/listing.php?'

RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

CATEGORIES_khar = {'parent_id%5B%5D=1&parent_id%5B%5D=9&parent_id%5B%5D=987': 11,                          #Аренда квартир долгосрочно
                   'parent_id%5B%5D=1&parent_id%5B%5D=8&parent_id%5B%5D=987': 11,                          #Аренда квартир посуточно
                   'parent_id%5B%5D=2&parent_id%5B%5D=11&parent_id%5B%5D=986': 24,                         #Аренда домов
                   'parent_id%5B%5D=9000&parent_id%5B%5D=9002&parent_id%5B%5D=1011': 27,                   #Аренда гаражей и паркингов
                   'parent_id%5B0%5D=4&parent_id%5B1%5D=65&parent_id%5B2%5D=all&parent_id%5B3%5D=999': 27, #Аренда коммерческой
                   'parent_id%5B%5D=1&parent_id%5B%5D=7&parent_id%5B%5D=984': 21,                          #Продажа квартир
                   'parent_id%5B%5D=2&parent_id%5B%5D=10&parent_id%5B%5D=985': 14,                         #Продажа домов
                   'parent_id%5B%5D=9000&parent_id%5B%5D=9001&parent_id%5B%5D=1010': 17,                   #Продажа гаражей и паркингов
                   'parent_id%5B0%5D=4&parent_id%5B1%5D=64&parent_id%5B2%5D=all&parent_id%5B3%5D=988': 17, #Продажа коммерческой
                   'parent_id%5B%5D=3&parent_id%5B%5D=983': 16                                             #Продажа участков
}
CATEGORIES_kiev = {'rid=51&p=': 11,                                                                        #Аренда квартир долгосрочно
                   'rid=38&p=1': 11,                                                                       #Аренда квартир посуточно
                   'rid=38&p=2': 11,
                   'parent_id%5B%5D=2&parent_id%5B%5D=11&parent_id%5B%5D=226': 24,                         #Аренда домов
                   'parent_id%5B%5D=9000&parent_id%5B%5D=9002&parent_id%5B%5D=9200': 27,                   #Аренда гаражей и паркингов
                   'parent_id%5B%5D=4&parent_id%5B%5D=65&parent_id%5B%5D=all&parent_id%5B%5D=7701': 27,    #Аренда коммерческой
                   'rid=129&p=': 21,                                                                       #Продажа квартир
                   'parent_id%5B%5D=2&parent_id%5B%5D=10&parent_id%5B%5D=165': 14,                         #Продажа домов
                   'parent_id%5B%5D=9000&parent_id%5B%5D=9001&parent_id%5B%5D=9100': 17,                   #Продажа гаражей и паркингов
                   'parent_id%5B%5D=4&parent_id%5B%5D=64&parent_id%5B%5D=all&parent_id%5B%5D=6601': 17,    #Продажа коммерческой
                   'parent_id%5B%5D=3&parent_id%5B%5D=12': 16                                              #Продажа участков
}

class FnSpider(Spider):
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
        super(FnSpider, self).__init__(*args, **kwargs)

    def prepare(self):
        try:
            f = open(os.path.join(MEDIA_ROOT, 'proxy', 'fine_all_proxy.txt'))
            self.proxy_list = f.readlines()
        finally:
            f.close()
            
    def create_grab_instance(self, **kwargs):
        g = super(FnSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=6, timeout=15)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        if self.city == 'kharkov':
            for category in CATEGORIES_khar:
                url = '%s%s' % (DOMEN, category)
                addition = {'category': category}
                yield Task('collect_adv_data', url, addition=addition)
        else:
            for category in CATEGORIES_kiev:
                if category.startswith('rid=51&p='):
                    i = 17
                    while i < 75:
                        category = 'rid=51&p=%s' %i
                        url = '%s%s' % (DOMEN, category)
                        i += 1
                elif category.startswith('rid=129&p='):
                    i = 15
                    while i < 50:
                        category = 'rid=129&p=%s&sort=0&pricemin=0&pricemax=100000&pricecur=2&rooms=0&acomm=off&stxt=' %i
                        url = '%s%s' % (DOMEN, category)
                        i += 1
                else:
                    url = '%s%s' % (DOMEN, category)
                    addition = {'category': category}
                yield Task('collect_adv_data', url, addition=addition)
            
    def task_collect_adv_data(self, grab, task):
        self.stats['taken'] += 1
        one = []
        url_adv = []
        for i in grab.doc.select('//@href'):
            one.append(i.text())
        for item in one:
            if item.startswith('view.php?ad_id=') and item not in url_adv:
                url_adv.append(item)
            else: continue
        for one_adv in url_adv:
            self.stats['processed'] += 1
            addition = task.get('addition')
            advert = Advert()
            if self.city == 'kharkov':
                advert.category_id = CATEGORIES_khar[addition['category']]
            else:
                advert.category_id = CATEGORIES_kiev[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = DOMEN[:13] + one_adv
            g = Grab()
            g.go(DOMEN[:13] + "print_" + one_adv)
            if g.doc.select("//td/p[contains(.,'%s')]" %u'Тел:').text():
                phones = g.doc.select("//td/p[contains(.,'%s')]" %u'Тел:').text()[5:]
                advert.raw_phones = phones
            g.go(DOMEN[:13] + one_adv)

            categories = g.doc.select('//div[@style="font-size: 11px;"]').text()

            if g.doc.select('//h1').text():
                title = g.doc.select('//h1').text()
                advert.title = title
            if g.doc.select('//p[@class="ad-price"]').text():
                numlist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
                price = ""
                for i in g.doc.select('//p[@class="ad-price"]').text():
                    if i in numlist:
                        price += i
                    else: continue
                if u'грн' in g.doc.select('//p[@class="ad-price"]').text():
                    if price:
                        advert.price_uah = int(price)
                else:
                    if price:
                        advert.price_usd = int(price)
            if g.doc.select('//p[@class="ad-desc"]').text():
                text = g.doc.select('//p[@class="ad-desc"]').text()
                advert.main_text = text
            # if g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Контакт').text():
            #     contact = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Контакт').text()[9:]
            #     advert.contact_name = contact
            if advert.category_id in [21, 11, 27, 17]:
                extra_object = ExtraFlat()
                if u"Этаж" in categories:
                    separator1 = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Этаж').text().find(":")
                    both = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Этаж').text()[separator1 + 2:]
                    separator2 = both.find("/")
                    floors = both[separator2 + 2:]
                    floor = both[:separator2 - 1]
                    extra_object.floors = floors
                    extra_object.floor = floor
                if u"Комнат" in categories:
                    rooms_number = g.doc.select('//p[@class="ad-contacts"]').text()[-1]
                    extra_object.rooms_number = rooms_number
                if u"Общая" in categories:
                    separator = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Общая площадь').text().find(":")
                    area = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Общая площадь').text()[separator + 2:-6]
                    extra_object.total_area = area
            if advert.category_id in [14, 24]:
                extra_object = ExtraHouse()
                if u"Этажность" in categories:
                    floors = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Этаж').text()[-1]
                    extra_object.floors = floors
                if u"Площадь дома" in categories:
                    separator = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Площадь дома').text().find(":")
                    area = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Площадь дома').text()[separator + 2:-6]
                    extra_object.total_area = area
                if u"Площадь участка" in categories:
                    separator = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" % u'Площадь участка').text().find(":")
                    area = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" % u'Площадь участка').text()[separator + 2:]
                    extra_object.lot_area = area
            if advert.category_id in [16]:
                extra_object = ExtraLot()
                if u"Площадь участка" in categories:
                    separator1 = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Площадь участка').text().find(":")
                    area = g.doc.select("//div[@style='font-size: 11px;']/p[contains(.,'%s')]" %u'Площадь участка').text()[separator1 + 2:]
                    extra_object.total_area = area
                if u"Под строительство" in categories:
                    granted = g.doc.select("//ul[@style='list-style-type: none']/li[contains(.,'%s')]" %u'Под').text()
                    extra_object.intended_purpose = granted
            if g.doc.select("//h3").text():
                if "," in g.doc.select("//h3").text():
                    subloc = g.doc.select("//h3").text()
                else:
                    separator = g.doc.select("//h3").text().find(" ")
                    subloc = g.doc.select("//h3").text()[:separator]
                advert.sublocality_id = SUB_FN[subloc]
            advert.metro_id = advert.detect_metro_id(self.metro_marker)
            same_adv = Advert.objects.filter(
                    category_id=advert.category_id,
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
                if i.text().startswith("./upload/pics/"):
                    img.append(i.text())
                else: continue
            for photo in img:
                photo_name_except = photo[14:-4]
                photo_link = '%s%s' % (DOMEN[:13], photo)
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