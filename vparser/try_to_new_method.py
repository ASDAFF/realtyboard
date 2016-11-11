# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from grab_new import Grab
from fake_useragent import UserAgent
import re
from grab.spider import Spider, Task
from vparser.utils import  HTM, save_to_main_base, up_date_for_fast_pars_all_cities, ProxyCheker, save_to_buffer, CustomizationForParser #,test_slando_proxy #CREDENTIALS, PROXY_PATH,
from board.models import City, Category, BigSublocality, Photo
from vparser.utils import parse_int
import logging
import json
from django.core.files.base import ContentFile
from hashlib import md5
import datetime
import time

#box
LOGIN_box = 'UA94671'
PASSWORD_box = '9X93nZXQ7h'
CREDENTIALS_box = LOGIN_box+':'+PASSWORD_box
PROXY_PATH_box = '/data/python/estate-kharkov.ci.ua/proxy/box_clear.txt'

#fine
LOGIN_fine = 'UA88061'
PASSWORD_fine = 'eIGF81N7mG'
CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
PROXY_PATH_fine = '/data/python/estate-kharkov.ci.ua/proxy/fine_clear.txt'

#elite
LOGIN_elite = 'UA111496'
PASSWORD_elite = 'WgN0eYlxA4'
CREDENTIALS_elite = LOGIN_elite+':'+PASSWORD_elite
PROXY_PATH_elite = '/data/python/estate-kharkov.ci.ua/proxy/elite_clear.txt'

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

LOCALITY={
    'kiev'   :['http://kiev.ko.slando.ua/nedvizhimost',      8],
    'kharkov':['http://kharkov.kha.slando.ua/nedvizhimost', 20]
}


VOCABULARY = [  # dic in list
    {'url': '%s/arenda-kvartir/?page=%s',       'pages': 10, 'cat': [21, 21]},
    {'url': '%s/arenda-komnat/?page=%s',        'pages': 10, 'cat': [21, 22]},
    {'url': '%s/arenda-domov/?page=%s',         'pages': 10, 'cat': [21, 24]},
    {'url': '%s/prodazha-kvartir/?page=%s',     'pages': 10, 'cat': [11, 11]},
    {'url': '%s/prodazha-komnat/?page=%s',      'pages': 10, 'cat': [11, 12]},
    {'url': '%s/prodazha-domov/?page=%s',       'pages': 10, 'cat': [14, 14]},
    {'url': '%s/prodazha-zemli/?page=%s',       'pages': 10, 'cat': [14, 16]},
    {'url': '%s/arenda-pomescheniy/?page=%s',   'pages': 10, 'cat': [27, 27]},
    {'url': '%s/prodazha-pomescheniy/?page=%s', 'pages': 10, 'cat': [17, 17]},
]




def save_to_base(grab, task, g2):
    # try:

    def type_rent():
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Тип аренды':
                if dd.text().split(':')[1] == u' Квартиры посуточно':
                    return 1
                elif dd.text().split(':')[1] == u' Квартиры с почасовой оплатой':
                    return 1
                elif dd.text().split(':')[1] == u' Койко-места':
                    return 1
                elif dd.text().split(':')[1] == u' Комнаты посуточно':
                    return 1
                elif dd.text().split(':')[1] == u' Дома посуточно, почасово':
                    return 1
                else:
                    return 2

    def region(city):
        try:
            region = grab.doc.select('//span[@class="show-map-link link gray cpointer"]').text().split(',')[1].replace(' ','')
            city_obj = City.objects.get(id=city.id)
            return BigSublocality.objects.get(city=city_obj, name__contains=region)
        except Exception, ex:
            print ex
            return False

    def room():
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Количество комнат':
                return dd.text().split(':')[1]
            elif dd.text().split(':')[0] == u'Всего комнат в квартире':
                return dd.text().split(':')[1]

    title = grab.doc.select('//h1').text()
    text = grab.doc.select('//div[@id="textContent"]').text()
    cost = grab.doc.select('//div[@class="pricelabel tcenter"]').text()
    deteil = grab.doc.select('//table[@class="details fixed marginbott20 margintop5"]').text()
    region_obj = region(task.city)
    phones = get_phone(g2)
    room_tot = room()
    rent = type_rent()

    print grab.response.url
    print 'title = ', title.encode('utf-8')
    print 'text = ', text.encode('utf-8')
    print 'cost = ', cost.encode('utf-8')
    print 'deteil = ', deteil.encode('utf-8')
    print 'phones = ', phones.encode('utf-8')
    print 'region = ', region_obj
    if room_tot:
        print 'room = ', room_tot.encode('utf-8')
    print 'type_rent = ', rent

    if task.city.id == 20:
        save_to_buffer(grab, task, phones, category=task.cat, moroz=task.moroz)

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
            print 'Advert.id = ', board.id
            photo = get_adv_photo(grab)
        return photo, board, True



def get_adv_photo(grab):
    photo = []
    try:
        photo.append(grab.doc.select('//div[@class="photo-glow"]/div[@class="photo-handler rel inlblk"]/img').attr('src'))
    except:
        pass
    for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
        photo.append(img.attr('src'))
    photo = set(photo)
    return photo


def get_adv_on_page(grab):
    h3_urls = []
    for elem in grab.doc.select('//h3/a'):
        h3_urls.append(elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls


def get_phone(grab):
    ajax_sl = "http://kiev.ko.slando.ua/ajax/misc/contact/phone/%s/"\
              % (re.findall(r'-ID(.*?).html', grab.response.url)[0])
    print 'advert_url = ', grab.response.url
    grab.go(ajax_sl)

    print 'phone_response_and_phone_url = ', grab.response.body, grab.response.url

    json_mas = json.loads(grab.response.unicode_body('utf-8'))
    phones = []
    phones.append(json_mas['value'])
    if 'span' in json_mas['value']:
        phones = re.findall(r'">(.*?)</', json_mas['value'])

    check_phone = ', '.join(phones)


    if not 'img' in check_phone:
        # return phones
        return check_phone

    else:
        return False


class SiteStructureParser(CustomizationForParser):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab()
        grab.load_proxylist(
            self.PROXY_PATH,
            'text_file',
            proxy_type='http',
            auto_init=False,
            auto_change=True
        )

        for link in VOCABULARY:
            url = link['url']
            pages = xrange(1, link['pages'])
            cat = Category.objects.get(id=link['cat'][1])
            moroz = link['cat'][0]
            city = City.objects.get(id=LOCALITY[self.city_pars][1])
            for page in pages:
                print 'number_of_pages=', page
                grab.change_proxy()
                grab.setup(
                    url=url % (LOCALITY[self.city_pars][0], page),
                    proxy_userpwd=self.CREDENTIALS,
                    hammer_mode=True,
                    hammer_timeouts=HTM,
                    user_agent=ua.random,
                    reuse_cookies=False
                )
                # check_proxies_for_slando(self, grab=grab, ua=ua.random, url=url % (LOCALITY[self.city_pars][0], page))
                print 'proxy before go of page list ', grab.config['proxy']
                yield Task('link_on_page', delay=3, grab=grab, cat=cat, city=city, moroz=moroz)


    # take all links on page
    def task_link_on_page(self, grab, task):
        print grab.config['proxy']
        ua = UserAgent()
        title = grab.doc.select('//title').text()
        print 'main title ===', title.encode('utf-8')
        h3_urls = get_adv_on_page(grab)
        if len(h3_urls):
            grab.load_proxylist(
                self.PROXY_PATH,
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
                    proxy_userpwd=self.CREDENTIALS,
                    user_agent=ua.random,
                    reuse_cookies=True)  # log_dir='vparser/tmp', reuse_cookies=True

                # check_proxies_for_slando(self, grab=grab, ua=ua.random, url=url)

                print 'proxy before go ', grab.config['proxy']
                yield Task('content', delay=3, grab=grab, cat=task.cat, city=task.city, moroz=task.moroz)

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
                        proxy_userpwd=self.CREDENTIALS,
                        reuse_cookies=True
                    )
                    print 'user_agent_for_img', grab.response.headers['user_agent']
                    # check_proxies_for_slando(self, grab=grab, ua=grab.response.headers['user_agent'], url=img)
                    yield Task('img', delay=3, grab=grab, board=board, i=i, cat=task.cat, city=task.city, moroz=task.moroz)

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
        path_tmp = '/data/python/estate-kharkov.ci.ua/vparser/tmp/%s/img/%s_%s.jpg' % (task.city.slug,task.board.id, task.i)
        grab.response.save(path_tmp, create_dirs=True)
        img = path_tmp
        dd = open(path_tmp)
        img = img.encode('utf-8')
        photo = Photo()
        photo.advert = task.board
        photo.photo.save("%s.%s" % (md5(img).hexdigest(),
                                    img[-3:]),
                           ContentFile(dd.read()))
        photo.save()
        print 'have to been save image - %s_%s' % (task.board.id, task.i)



def test_slandos():

    ua = UserAgent()
    grab = Grab(timeout=30, connect_timeout =10,  log_file='/data/python/estate-kharkov.ci.ua/vparser/tmp/pars/log.html')
    grab.setup(proxy='46.148.30.123:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)  # , log_dir='vparser/tmp'
    # grab.go('http://kiev.ko.slando.ua/obyavlenie/predlagaetsya-v-arendu-posutochno-v-kieve-kvartira-odnokomnatnaya-po-ulits-ID75E19.html#a025724d26')
    grab.go('http://kharkov.kha.olx.ua/obyavlenie/sdam-komnatu-posutochno-studentam-zaochnikam-na-vremya-sessii-ID7wtX5.html#d8c94fe691;promoted')
    # grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')



    def get_adv_photo(grab):
        photo = []
        try:
            photo.append(grab.doc.select('//div[@class="photo-glow"]/div[@class="photo-handler rel inlblk"]/img').attr('src'))
        except:
            pass
        for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
            photo.append(img.attr('src'))
        photo = set(photo)
        return photo

    print get_adv_photo(grab)