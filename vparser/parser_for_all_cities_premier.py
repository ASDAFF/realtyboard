# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from grab import Grab
from fake_useragent import UserAgent
import re, os
from grab.spider import Spider, Task
from vparser.utils import  HTM, save_to_main_base, up_date_for_fast_pars_all_cities
from vparser.utils import CustomizationForParser, ProxyCheker, save_to_buffer #,test_slando_proxy #CREDENTIALS, PROXY_PATH,
from board.models import City, Category, BigSublocality, Photo
from vparser.utils import parse_int
import logging
import json
from django.core.files.base import ContentFile
from hashlib import md5
import datetime
import time

from realtyboard.settings import MEDIA_ROOT, PROJECT_PATH

#box
LOGIN_box = 'UA94671'
PASSWORD_box = '9X93nZXQ7h'
CREDENTIALS_box = LOGIN_box+':'+PASSWORD_box
PROXY_PATH_box = '%s/proxy/box_clear.txt' % MEDIA_ROOT

#fine
LOGIN_fine = 'UA88061'
PASSWORD_fine = 'eIGF81N7mG'
CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
PROXY_PATH_fine = '%s/proxy/fine_clear.txt' % MEDIA_ROOT

#elite
LOGIN_elite = 'UA111496'
PASSWORD_elite = 'WgN0eYlxA4'
CREDENTIALS_elite = LOGIN_elite+':'+PASSWORD_elite
PROXY_PATH_elite = '%s/proxy/elite_clear.txt' % MEDIA_ROOT

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

LOCALITY={
    # 'kiev'   :[[u'http://dom.ria.com/ru/Каталог',u'Киевская', u'Киев'],      8],
    'kharkov':["There aren't need here", 20]
}


VOCABULARY = [
    # аренда жилая
    {'url': u'http://premier.ua/subcategory-52-page-%s.aspx',       'pages': 30, 'cat': [21, 21]  ,'room': False},  # аренда посуточно
    {'url': u'http://premier.ua/subcategory-54-page-%s.aspx',       'pages': 30, 'cat': [21, 21]  ,'room': '1'},  # аренда 1к кв
    {'url': u'http://premier.ua/subcategory-55-page-%s.aspx',       'pages': 30, 'cat': [21, 21]  ,'room': '2'},  # аренда 2к кв
    {'url': u'http://premier.ua/subcategory-56-page-%s.aspx',       'pages': 21, 'cat': [21, 21]  ,'room': False},  # аренда многокомнатные элитные
    {'url': u'http://premier.ua/subcategory-57-page-%s.aspx',       'pages': 21, 'cat': [21, 22]  ,'room': False},  # аренда гостики комнаты
    {'url': u'http://premier.ua/subcategory-58-page-%s.aspx',       'pages': 10, 'cat': [21, 24]  ,'room': False},  # аренда дома
    # продажа квартиры гостинки
    {'url': u'http://premier.ua/subcategory-70-page-%s.aspx',       'pages': 26, 'cat': [11, 11]  ,'room': False},  # квартиры новострой
    {'url': u'http://premier.ua/subcategory-80-page-%s.aspx',       'pages': 30, 'cat': [11, 11]  ,'room': '1'},  # 1к квартиры
    {'url': u'http://premier.ua/subcategory-100-page-%s.aspx',      'pages': 30, 'cat': [11, 11]  ,'room': '2'},  # 2к квартиры
    {'url': u'http://premier.ua/subcategory-120-page-%s.aspx',      'pages': 30, 'cat': [11, 11]  ,'room': '3'},  # 3к квартиры
    {'url': u'http://premier.ua/subcategory-140-page-%s.aspx',      'pages': 21, 'cat': [11, 11]  ,'room': '4'},  # 4к квартиры
    {'url': u'http://premier.ua/subcategory-160-page-%s.aspx',      'pages': 31, 'cat': [11, 12]  ,'room': False},  # гостинки комнаты
    # продажа дома участки
    {'url': u'http://premier.ua/subcategory-165-page-%s.aspx',      'pages': 19, 'cat': [14, 16]  ,'room': False},  # участки Харьков
    {'url': u'http://premier.ua/subcategory-169-page-%s.aspx',      'pages': 35, 'cat': [14, 14]  ,'room': False},  # дома Харьков
    {'url': u'http://premier.ua/subcategory-166-page-%s.aspx',      'pages': 21, 'cat': [14, 16]  ,'room': False},  # участки пригород
    {'url': u'http://premier.ua/subcategory-181-page-%s.aspx',      'pages': 35, 'cat': [14, 14]  ,'room': False},  # дома пригород
    # аренда коммерческой недвижимости
    {'url': u'http://premier.ua/subcategory-20-page-%s.aspx',       'pages': 35, 'cat': [27, 27]  ,'room': False},
    # продажа коммерческой недвижимости
    {'url': u'http://premier.ua/subcategory-31-page-%s.aspx',       'pages': 30, 'cat': [17, 17]  ,'room': False},
    # клиенты
    {'url': u'http://premier.ua/subcategory-53-page-%s.aspx',       'pages': 11, 'cat': [100, 41] ,'room': False},  # сниму жилье
    {'url': u'http://premier.ua/subcategory-60-page-%s.aspx',       'pages': 10, 'cat': [100, 31] ,'room': False},  # куплю жилье
    {'url': u'http://premier.ua/subcategory-30-page-%s.aspx',       'pages': 2, 'cat': [100, 37]  ,'room': False},  # куплю коммерческую
]



def save_to_base(grab, task, g2):

    def type_rent(grab):
        try:
            if grab.doc.select('//li[@class="last"]').text() == u'Посуточно':
                return 1
            else:
                return 2
        except Exception, ex:
            print ex
            return 2

    def region(city):
            return False

    def room():
        return task.room if task.room else False

    def text():
        return grab.doc.select('//td[@colspan="2"]').text()

    print grab.response.url

    title = grab.doc.select("//title").text()
    text = text()
    cost = grab.doc.select('//td')[2].text()
    region_obj = region(task.city)
    phones = get_phone(grab)
    room_tot = room()
    rent = type_rent(grab)

    print 'title = ', title.encode('utf-8')
    print 'text = ', text.encode('utf-8')
    print 'cost = ', cost.encode('utf-8')
    print 'phones = ', phones
    print 'region = ', region_obj
    print 'room = ', room_tot
    print 'type_rent = ', rent

    # if task.city.id == 20:
    #     save_to_buffer(grab, task, phones, category=task.cat, moroz=task.moroz)

    # locality='http://kiev.ko.slando.ua/'
    print LOCALITY[task.city.slug][0]
    if phones:
        board = save_to_main_base(num_city=task.city,
                          text=text,
                          title=title,
                          category=task.cat,
                          raw_phones=phones,
                          cost=cost,
                          link=grab.response.url,
                          locality=LOCALITY[task.city.slug][0],
                          region=region_obj,
                          room = room_tot,
                          object_type = rent
        )

        photo = False
        if board:
            photo = get_adv_photo(grab)
        return photo, board, True



def get_adv_photo(grab):
    photo = []
    for img in grab.doc.select('//div[@class="adv-imgs"]/a'):
        tt = img.attr('href')
        tt = 'http://premier.ua%s' % tt
        photo.append(tt)
    photo = set(photo)
    return photo

def get_adv_on_page(grab=None):
    h3_urls = []
    for elem in grab.doc.select('//td[@class="adv-title"]/a'):
        h3_urls.append('http://premier.ua%s' % elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls

def get_phone(grab):
    phones = []
    for t, p in enumerate(grab.doc.select('//tr/td')):
        if p.text() == u'Телефон:':
            phone1 = str(parse_int(grab.doc.select('//tr/td')[t+1].text()))
            if phone1.isdigit() and phone1 != '0':
                phones.append(phone1)
            phone2 = str(parse_int(grab.doc.select('//tr/td')[t+3].text()))
            if phone2.isdigit() and phone2 != '0':
                phones.append(phone2)
    return ','.join(phones)


class SiteStructureParser(CustomizationForParser):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab()
        grab.load_proxylist(
            self.PROXY_PATH_hideme,
            'text_file',
            proxy_type='http',
            auto_init=False,
            auto_change=True
        )

        for link in VOCABULARY:
            url = link['url']
            room = link['room']
            # part_url = LOCALITY[self.city_pars]
            pages = xrange(1, link['pages'])
            cat = Category.objects.get(id=link['cat'][1])
            moroz = link['cat'][0]
            city = City.objects.get(id=LOCALITY[self.city_pars][1])
            for page in pages:
                print 'number_of_pages=', page
                grab.change_proxy()
                grab.setup(
                    url=url % page,
                    # proxy_userpwd=self.CREDENTIALS,
                    hammer_mode=True,
                    hammer_timeouts=HTM,
                    user_agent=ua.random,
                    reuse_cookies=False
                )
                # check_proxies_for_slando(self, grab=grab, ua=ua.random, url=url % (LOCALITY[self.city_pars][0], page))
                print 'proxy before go of page list ', grab.config['proxy']
                yield Task('link_on_page', delay=4, grab=grab, cat=cat, city=city, moroz=moroz, room=room)


    # take all links on page
    def task_link_on_page(self, grab, task):
        print grab.config['proxy']
        ua = UserAgent()
        title = grab.doc.select('//title').text()
        print 'main title ===', title.encode('utf-8')
        h3_urls = get_adv_on_page(grab)
        if len(h3_urls):
            grab.load_proxylist(
                self.PROXY_PATH_hideme,
                'text_file',
                proxy_type='http',
                auto_init=False, auto_change=True
            )
            for url in h3_urls:
                if up_date_for_fast_pars_all_cities(url, task.city):
                    continue
                grab.change_proxy()
                grab.setup(
                    url=url,
                    hammer_mode=True,
                    hammer_timeouts=HTM,
                    # proxy_userpwd=self.CREDENTIALS,
                    user_agent=ua.random,
                    reuse_cookies=True)  # log_dir='vparser/tmp', reuse_cookies=True

                # check_proxies_for_slando(self, grab=grab, ua=ua.random, url=url)

                print 'proxy before go ', grab.config['proxy']
                yield Task('content', delay=4, grab=grab, cat=task.cat, city=task.city, moroz=task.moroz, room=task.room)

    #grab content
    def task_content(self, grab, task):
        print grab.config['proxy']
        g2 = grab.clone()
        photo, board, status = save_to_base(grab, task, g2)
        if status:
            if photo:
                for i, img in enumerate(photo):
                    print u'has sent to task - %s' % i
                    grab.setup(
                        url=img,
                        hammer_mode=True,
                        hammer_timeouts=HTM,
                        # proxy_userpwd=self.CREDENTIALS,
                        reuse_cookies=True
                    )
                    print 'user_agent_for_img', grab.response.headers['user_agent']
                    yield Task('img', delay=4, grab=grab, board=board, i=i, cat=task.cat, city=task.city, moroz=task.moroz, room=task.room)
        # else:
        #     print 'REPEAT----------------------'
        #     ua = UserAgent()
        #     grab.load_proxylist(
        #         PROXY_PATH,
        #         'text_file',
        #         proxy_type='http',
        #         auto_init=False,
        #         auto_change=True
        #     )
        #     grab.setup(
        #         url=grab.response.url,
        #         proxy_userpwd=CREDENTIALS,
        #         hammer_mode=True,
        #         hammer_timeouts=HTM,
        #         user_agent=ua.random,
        #         reuse_cookies=True
        #         # , log_dir='vparser/tmp'
        #     )
        #     grab.change_proxy()
        #     yield Task('content', grab=grab, task_try_count=task.task_try_count + 1, cat=task.cat, city=task.city)

    def task_img(self, grab, task):
        path_tmp = '%s/vparser/tmp/%s/img/%s_%s.jpg' % (
            os.path.split(PROJECT_PATH)[0], task.city.slug,task.board.id, task.i)
        grab.response.save(path_tmp, create_dirs=True)
        img = path_tmp
        dd = open(path_tmp)
        img = img.encode('utf-8')
        photo = Photo()
        photo.advert = task.board
        photo.photo.save("%s.%s" % (md5(img).hexdigest(), img[-3:]),
                         ContentFile(dd.read()))
        photo.save()
        print 'have to been save image - %s_%s' % (task.board.id, task.i)



def test_premier():

    ua = UserAgent()
    grab = Grab(timeout=30, 
                connect_timeout =10,  
                log_file='%s/vparser/tmp/pars/log.html' % os.path.split(PROJECT_PATH)[0])
    # grab.setup(proxy='91.207.61.69:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)  # , log_dir='vparser/tmp'
    # grab.setup(proxy='94.154.222.95:8080', proxy_type='http')  # , log_dir='vparser/tmp'
    # grab.go('http://kiev.ko.slando.ua/obyavlenie/predlagaetsya-v-arendu-posutochno-v-kieve-kvartira-odnokomnatnaya-po-ulits-ID75E19.html#a025724d26')

    grab.go('http://premier.ua/adv-8865396.aspx')

    # def type_rent(grab):
    #     try:
    #         if grab.doc.select('//li[@class="last"]').text() == u'Посуточно':
    #             return 1
    #         else:
    #             return 2
    #     except Exception, ex:
    #         print ex
    #         return 2
    #
    # def region(city):
    #         return False
    #
    # def room():
    #     return False

    def text():
        return grab.doc.select('//td[@colspan="2"]').text()
    print  text()

    # print grab.response.url
    #
    # title = grab.doc.select("//title").text()
    # # text = text()
    # # cost = grab.doc.select('//td')[2].text()
    # # region_obj = region(task.city)
    # phones = get_phone(grab)
    # room_tot = room()
    # rent = type_rent(grab)
    #
    # print 'title = ', title.encode('utf-8')
    # # print 'text = ', text.encode('utf-8')
    # # print 'cost = ', cost.encode('utf-8')
    # print 'phones = ', phones
    # # print 'region = ', region_obj
    # print 'room = ', room_tot
    # print 'type_rent = ', rent

    # grab.go('http://premier.ua/adv-8853714.aspx')
    # from time import sleep
    #
    # for tt in xrange(1, 10):
    #     sleep(1)
    #     grab.go('http://premier.ua/adv-8853714.aspx')
    #     print grab.doc.select('//title').text()
    # # grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')






    # print grab.doc.select('//div[@class="price-seller"]').text()