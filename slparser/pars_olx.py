# -*- coding: utf-8 -*-
import csv, datetime, hashlib, json, os, pytz, random, re, urllib

from django.core.files.base import ContentFile
from django.utils import timezone
from grab.spider import Spider, Task
from grab.error import GrabNetworkError
from time import sleep

from board.models import Advert, City, Phone, Photo, SublocalityDetect
from board.models import ExtraCommercial, ExtraFlat
from board.models import ExtraHouse, ExtraLot, ExtraRent, BigSublocality, MetroDetect
from personal.models import UserData
from realtyboard.settings import USD_UAH, MEDIA_ROOT, PROXY_CREDENTIALS

import logging
logging.basicConfig(level=logging.DEBUG)

# XPath class selector
xpcs = lambda x: "contains(concat(' ', normalize-space(@class), ' '), ' %s ')" % x

RE_RECENTLY = re.compile(ur'^([а-яА-Я\s]+)(\d{2}):(\d{2})')
# RE_LONG_AGO = re.compile(ur'^(\d{2})(?:\s*)([а-яА-Я]{3,8})')
RE_LIST_URL = re.compile(r'^.+/\?page=\d{1,2}$')
RE_LIST_NUMBER = re.compile(r'(?<=page\=)\d{1,2}')
RE_ADV_LINK = re.compile(r'^[^#]+')
RE_ADV_OLX_ID = re.compile(r'(?<=ID)\w+')
RE_PHONE = re.compile(r'[\d(]\d[\s\d()-]{3,16}')
RE_SPACE = re.compile(r'\s')
RE_NON_DIGIT = re.compile(r'\D+')
RE_DIGIT = re.compile(r'\d+')
RE_EXTENTION = re.compile(r'[a-zA-Z]+$')

SUB_IF = {
    u'Киевский' : 3005,
    u'Дзержинский' : 3004,
    u'Коминтерновский' : 3006,
    u'Ленинский' : 3007,
    u'Московский' : 3008,
    u'Октябрьский' : 3012,
    u'Орджоникидзевский' : 3009,
    u'Фрунзенский' : 3010,
    u'Червонозаводской' : 3011,
    u'Индустриальный' : 3009,
    u'Холодногорский' : 3007,
    u'Шевченковский' : 3004,
}

DOMEN_PHONE = {'kharkov':'http://kharkov.kha.olx.ua',
          'kiev': 'http://kiev.ko.olx.ua'}

DOMEN = "https://www.olx.ua"

REGION = {'kharkov':'kharkov',
        'kiev': 'kiev'}

# DOMEN = {'kharkov':'http://kharkov.kha.olx.ua',
#          'kiev': 'http://kiev.ko.olx.ua'}

CATEGORIES= {'arenda-kvartir': 21,
             'arenda-komnat': 22,
             'arenda-domov': 24,
             'arenda-zemli': 26,
             'arenda-pomescheniy': 27,
             'arenda-garazhey-stoyanok': 27,
             'prodazha-kvartir': 11,
             'prodazha-komnat': 12,
             'prodazha-domov': 14,
             'prodazha-zemli': 16,
             'prodazha-pomescheniy': 17,
             'prodazha-garazhey-stoyanok': 17,
             }

class OlxSpider(Spider):
    sublocality_marker = None
    proxy_list = []
    # lexxx id 8606
    author_id = 8606
    stats = {'processed': 0, 'taken': 0, 'omited': 0,
             'without_phone': 0, 'saved': 0}

    def __init__(self, *args, **kwargs):
        self.city = kwargs.pop('city')
        self.city_id = City.objects.filter(
            slug=self.city)[:1].values_list('id', flat=True)[0]
        self.sublocality_marker = SublocalityDetect.objects.filter(
                city_id=self.city_id)
        if self.city_id in [20, 8, 3]:
            self.metro_marker = MetroDetect.objects.filter(city_id=self.city_id)
        # depth should be set in minutes
        self.start_time = datetime.datetime.now()
        self.depth = datetime.timedelta(minutes=int(kwargs.pop('depth', 30)))
        self.stop_time = self.start_time - self.depth
        self.proxy_credentials = PROXY_CREDENTIALS['fine']
        # print '//////////stop time ', self.stop_time, '//////////////////'
        super(OlxSpider, self).__init__(*args, **kwargs)

    def prepare(self):
        try:
            f = open(os.path.join(MEDIA_ROOT, 'proxy', 'proxy_olx.txt'))
            self.proxy_list = f.readlines()
        finally:
            f.close()

    def create_grab_instance(self, **kwargs):
        g = super(OlxSpider, self).create_grab_instance(**kwargs)
        g.setup(connect_timeout=10, timeout=30)
        g.proxylist.load_list(self.proxy_list,
            proxy_userpwd=self.proxy_credentials)
        return g

    def task_generator(self):
        for category in CATEGORIES:
            sleep(1)
            url = '%s/nedvizhimost/%s/%s' % (DOMEN,category, REGION[self.city])
            # url = '%s/nedvizhimost/%s/' % (DOMEN[self.city],category)
            addition = {'category': category}
            yield Task('collect_adv_links', url, addition=addition)

    def task_collect_adv_links(self, grab, task):
        # print "//////////parse adv list task///////////"
        addition = task.get('addition')
       
        adv_lists = grab.doc.select("//div[%s]/table" % xpcs('listHandler'))
        if len(adv_lists) == 2:
             top_list, usual_list = adv_lists
        else:
            usual_list = adv_lists[0]
            top_list = ()
        if top_list:
            top_list = self.prepare_adv_links(top_list, addition)
        usual_list, next_page = self.prepare_adv_links(usual_list, addition, True)
        
        for adv_list in (top_list, usual_list):
            for adv_link in adv_list:
                yield Task('collect_adv_data', adv_link,
                           delay=random.uniform(1,5),
                           addition=addition)
        if next_page:
            # print '/////////go to next page////////////////'
            if RE_LIST_URL.match(grab.config['url']):
                next_page_number = str(int(
                    RE_LIST_NUMBER.search(grab.config['url']).group()) + 1)
                url = RE_LIST_NUMBER.sub(next_page_number, grab.config['url'])
            else:
                url = grab.config['url'] + '?page=2'
                # print url
                yield Task('collect_adv_links', url, addition=addition)

    def task_collect_adv_data(self, grab, task):
        # print "////////collect adv data////////////"
        # if there is no phone it doesn't make sense to take other data
        sleep(1)
        self.stats['taken'] += 1
        if grab.doc.select("//li[%s]" % xpcs('link-phone')):
            addition = task.get('addition')

            # print '////////create new Advert object///////////'
            advert = Advert()
            advert.category_id = CATEGORIES[addition['category']]
            advert.city_id = self.city_id
            advert.author_id = self.author_id
            advert.link = RE_ADV_LINK.search(grab.config['url']).group()
            advert.title = grab.doc.select("//h1").text()
            price = grab.doc.select(
                "//div[%s]/strong" % xpcs('pricelabel')).text()
            currency = 'uah' if u'грн' in price else 'usd'
            if currency == 'uah':
                advert.price_uah = int(RE_NON_DIGIT.sub('', price))
                advert.price_usd = advert.price_uah / USD_UAH
            else:
                advert.price_usd = int(RE_NON_DIGIT.sub('', price))
                advert.price_uah = advert.price_usd * USD_UAH
            # think about location
            advert.main_text = grab.doc.select("//div[@id='textContent']/p").text()
            address = grab.doc.select(
                "//span[%s]/strong" % xpcs('show-map-link')).text().split(',')
            if len(address) > 3:
                advert.street = address[3]
            if self.city_id == 8 and len(address) >= 3:
                kiev_big_subloc = BigSublocality.objects.filter(
                    name__startswith=address[2].strip()).first()
                if kiev_big_subloc:
                    advert.big_sublocality_id = kiev_big_subloc.id

            extra_action = None
            if advert.category_id in (21, 22, 24, 26, 27):
                extra_action = ExtraRent()
            if advert.category_id in (11, 12, 21, 22):
                extra_object = ExtraFlat()
            if advert.category_id in (14, 24):
                extra_object = ExtraHouse()
            if advert.category_id in (16, 26):
                extra_object = ExtraLot()
            if advert.category_id in (17, 27):
                extra_object = ExtraCommercial()
                
            if addition['category'] in (
                    'arenda-kvartir', 'prodazha-kvartir', 'prodazha-komnat'):
                rooms_number = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Количество комнат')
                if rooms_number:
                    extra_object.rooms_number = RE_DIGIT.search(
                        rooms_number.select(".//td[@class='value']").text()
                    ).group()
                total_area = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Общая площадь')
                if total_area:
                    extra_object.total_area = RE_DIGIT.search(
                        total_area.select(".//td[@class='value']").text()
                    ).group()
                floor = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Этаж')
                if floor:
                    extra_object.floor = RE_DIGIT.search(
                        floor.select(".//td[@class='value']").text()
                    ).group()
                floors = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Этажность дома')
                if floors:
                    extra_object.floors = RE_DIGIT.search(
                        floors.select(".//td[@class='value']").text()
                    ).group()

            if 'arenda' in addition['category']:
                rent_term = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Тип аренды')
                rent_term = rent_term.select(
                    ".//td[@class='value']"
                ).text() if rent_term else u'Долгосрочная аренда'
                extra_action.term = 2 if u'Долгосрочная' in rent_term else 1

            if addition['category'] == 'arenda-komnat':
                rooms_number = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Всего комнат')
                if rooms_number:
                    extra_object.rooms_number = RE_DIGIT.search(
                        rooms_number.select(".//td[@class='value']").text()
                    ).group()

            if addition['category'] in ('arenda-domov', 'prodazha-domov'):
                total_area = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Площадь дома')
                if total_area:
                    extra_object.total_area = RE_DIGIT.search(
                        total_area.select(".//td[@class='value']").text()
                    ).group()

            if addition['category'] == 'prodazha-domov':
                house_type = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Тип дома')
                house_type = house_type.select(
                    ".//td[@class='value']").text() if house_type else None
                extra_object.house_type = 2 if house_type == u'Продажа дач' else 1

            if addition['category'] == 'prodazha-kvartir':
                building = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Тип квартиры')
                building = building.select(
                    ".//td[@class='value']").text() if building else ''
                if u'Новостройки' in building:
                    extra_object.new_building = True

            if addition['category'] == 'prodazha-zemli':
                lot_purpose = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Тип участка')
                lot_purpose = lot_purpose.select(
                    ".//td[@class='value']").text() if lot_purpose else ''
                if u'сад / огород' in lot_purpose:
                    extra_object.intended_purpose = 'садоводство'
                elif u'индивидуальное строительство' in lot_purpose:
                    extra_object.intended_purpose = 'под застройку'
                elif u'сельскохозяйственного назначения' in lot_purpose:
                    extra_object.intended_purpose = u'ОСГ(особисте селянське господарство)'
                elif u'промышленного назначения' in lot_purpose:
                    extra_object.intended_purpose = u'коммерческого назначения'
                lot_area = grab.doc.select(
                    "//table[@class='item'][contains(., '%s')]" % u'Площадь')
                lot_area = RE_DIGIT.search(
                    lot_area.select(".//td[@class='value']").text()
                ).group() if lot_area else None
                if lot_area:
                    extra_object.lot_unit = u'соток'

            photo_links = grab.doc.select("//img[%s]" % xpcs('bigImage'))
            photos = []
            # print '//////amount of photos %s/////////' % len(photo_links)
            if photo_links:
                photo_grab = grab.clone()
                photo_grab.setup(proxy_auto_change=False,
                                 reuse_referer=False)
                sleep(0.2)
                photo_links2 = []
                for photo_link in photo_links:
                    try:
                        photo_grab.go(photo_link.attr('src'))
                        if photo_grab.response.code == 200 and \
                               re.match('image/', photo_grab.response.headers['Content-Type']):
                            photos.append({
                                'body': photo_grab.response.body,
                                'extention': RE_EXTENTION.search(photo_grab.config['url']).group()
                            })
                    except GrabNetworkError as error:
                        # print('////error while taking photo////')
                        photo_links2.append(photo_link)
                # print('////one more try///')
                # print(len(photo_links2))
                for photo_link in photo_links2:
                    photo_grab.go(photo_link.attr('src'))
                    if photo_grab.response.code == 200 and \
                           re.match('image/', photo_grab.response.headers['Content-Type']):
                        photos.append({
                            'body': photo_grab.response.body,
                            'extention': RE_EXTENTION.search(photo_grab.config['url']).group()
                        })

            phone_raw = self.take_phone(grab)
            phone_in_text = advert.detect_phone()
            if phone_raw and phone_in_text:
                phone_raw = phone_raw + ',' + ','.join(phone_in_text)
            elif phone_in_text:
                phone_raw = ','.join(phone_in_text)
            if phone_raw:
                advert.raw_phones = phone_raw
                subloc = None
                sub_if = grab.doc.select("//strong[@class='c2b small']").text()
                for sub_one in SUB_IF:
                    if sub_one in sub_if:
                        subloc = sub_one
                if subloc is not None:
                    advert.sublocality_id = int(SUB_IF[subloc])
                else:
                    advert.sublocality_id = advert.detect_sublocality_id(
                                                self.sublocality_marker) 
                if self.metro_marker:
                    advert.metro_id = advert.detect_metro_id(self.metro_marker)
                # print '//////////SAVE ADVERT/////////'
                advert.save()
                self.stats['saved'] += 1
                for i, img in enumerate(photos):
                    photo = Photo(advert_id=advert.id)
                    file_name = '%s.%s' % (
                        hashlib.md5(grab.config['referer']+str(i)).hexdigest(),
                        img['extention']
                    )
                    photo.photo.save(file_name, ContentFile(img['body']))
                if self.extra_has_values(extra_object):
                    extra_object.advert = advert
                    extra_object.save()
                if extra_action:
                    extra_action.advert = advert
                    extra_action.save()
        else:
            self.stats['without_phone'] += 1

    def prepare_adv_links(self, adv_list, addition, get_next=False):
        next_page = True
        link_list = []
        for adv_block in adv_list.select(".//td[%s]" % xpcs('offer')):
            up_time, adv_link = self.processing_adv_block(adv_block)
            self.stats['processed'] += 1
            if up_time > self.stop_time:
                # print '////////////check if advert present in database///////////'
                same_adv = Advert.objects.filter(
                    category_id=CATEGORIES[addition['category']],
                    author_id=self.author_id,
                    city_id=self.city_id,
                    link=RE_ADV_LINK.search(adv_link).group()
                ).only('date_of_update').first()
                if same_adv:
                    # print '//////////omit this advert not new//////////////////'
                    self.stats['omited'] += 1
                    if same_adv.date_of_update < (
                            timezone.now() - datetime.timedelta(hours=20)):
                        same_adv.date_of_update = timezone.now()
                        same_adv.save()
                else:
                    link_list.append(adv_link)
            else:
                # print "///////old adverts going////////"
                self.stats['omited'] += 1
                next_page = False
                break
        if get_next:
            return link_list, next_page
        else:
            return link_list

    def processing_adv_block(self, adv_block):
        # print '///////////processing adv block///////////'
        up_time = adv_block.select(".//p[%s]" % xpcs('x-normal')).text()
        price = adv_block.select(".//p[@class='price']/strong").text()
        adv_link = adv_block.select(".//h3/a").attr('href')
        match = RE_RECENTLY.match(up_time)
        if match:
            up_time = datetime.datetime.now().replace(
                hour=int(match.group(2)), minute=int(match.group(3)))
            if match.group(1) == u'Вчера':
                up_time -= datetime.timedelta(days=1)
        else:
            up_time = datetime.datetime.now() - datetime.timedelta(days=3)
        return up_time, adv_link

    def take_phone(self, grab):
        # print '///////////////get phone//////////////'
        adv_olx_id = RE_ADV_OLX_ID.search(grab.config['url']).group()
        phone_grab = grab.clone()
        phone_grab.setup(proxy_auto_change=False,
                         headers={'X-Requested-With': 'XMLHttpRequest'},
                         reuse_referer=False)
        phone_grab = self.take_phone_go(phone_grab, adv_olx_id)
        if phone_grab:
            # print phone_grab.response.body
            phone_raw = json.loads(phone_grab.response.body)['value']
            phone_raw = ','.join(RE_PHONE.findall(phone_raw))
            return phone_raw

    def take_phone_go(self, phone_grab, adv_olx_id, tries_count=0):
        # print '//////////phone grab go/////////', tries_count
        sleep(random.uniform(1,4))
        try:
            phone_grab.go(
                '%s/ajax/misc/contact/phone/%s/' % (DOMEN_PHONE[self.city], adv_olx_id))
                # '%s/ajax/misc/contact/phone/%s/' % (DOMEN[self.city], adv_olx_id))
        except GrabNetworkError as error:
            print '///////ERROR/////////GrabNetworkError////////ERROR///////'
            print error
            # if tries_count < 2:
            #     tries_count += 1
            #     self.take_phone_go(phone_grab, adv_olx_id, tries_count)
            # elif tries_count < 4:
            #     print '///////change ptoxy for phone_grab////////'
            #     phone_grab.setup(proxy_auto_change=True)
            #     tries_count += 1
            #     self.take_phone_go(phone_grab, adv_olx_id, tries_count)
            # else:
            #     return None
        else:
            # print '////tries_count %s' % tries_count
            return phone_grab

    def extra_has_values(self, extra):
        for field in extra.__dict__:
            if field not in ('_state', 'advert_id', 'id'):
                if extra.__dict__[field]:
                    return True
        # print '///extra has no data////'
