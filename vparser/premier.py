# -*- coding: utf-8 -*-
from sre_parse import isdigit
from grab import Grab
import re
import logging
from grab.spider import Spider, Task
from importdb.models import Slandos
from vparser.utils import parse_int
from vparser.slando import CREDENTIALS, up_date_for_fast_pars, PROXY_PATH
import datetime
import sys, os

from realtyboard.settings import PROJECT_PATH

PROXY_PATH = '/data/python/track.ci.ua/proxy.txt'

VOCABULARY = [
    # аренда жилая
    {'url': u'http://premier.ua/subcategory-52-page-%s.aspx',       'pages': 30, 'cat': [21, 21]},  # аренда посуточно
    {'url': u'http://premier.ua/subcategory-54-page-%s.aspx',       'pages': 60, 'cat': [21, 21]},  # аренда 1к кв
    {'url': u'http://premier.ua/subcategory-55-page-%s.aspx',       'pages': 40, 'cat': [21, 21]},  # аренда 2к кв
    {'url': u'http://premier.ua/subcategory-56-page-%s.aspx',       'pages': 21, 'cat': [21, 21]},  # аренда многокомнатные элитные
    {'url': u'http://premier.ua/subcategory-57-page-%s.aspx',       'pages': 21, 'cat': [21, 22]},  # аренда гостики комнаты
    {'url': u'http://premier.ua/subcategory-58-page-%s.aspx',       'pages': 10, 'cat': [21, 24]},  # аренда дома
    # продажа квартиры гостинки
    {'url': u'http://premier.ua/subcategory-70-page-%s.aspx',       'pages': 26, 'cat': [11, 11]},  # квартиры новострой
    {'url': u'http://premier.ua/subcategory-80-page-%s.aspx',       'pages': 50, 'cat': [11, 11]},  # 1к квартиры
    {'url': u'http://premier.ua/subcategory-100-page-%s.aspx',      'pages': 50, 'cat': [11, 11]},  # 2к квартиры
    {'url': u'http://premier.ua/subcategory-120-page-%s.aspx',      'pages': 50, 'cat': [11, 11]},  # 3к квартиры
    {'url': u'http://premier.ua/subcategory-140-page-%s.aspx',      'pages': 21, 'cat': [11, 11]},  # 4к квартиры
    {'url': u'http://premier.ua/subcategory-160-page-%s.aspx',      'pages': 51, 'cat': [11, 12]},  # гостинки комнаты
    # продажа дома участки
    {'url': u'http://premier.ua/subcategory-165-page-%s.aspx',      'pages': 19, 'cat': [14, 16]},  # участки Харьков
    {'url': u'http://premier.ua/subcategory-169-page-%s.aspx',      'pages': 65, 'cat': [14, 14]},  # дома Харьков
    {'url': u'http://premier.ua/subcategory-166-page-%s.aspx',      'pages': 21, 'cat': [14, 16]},  # участки пригород
    {'url': u'http://premier.ua/subcategory-181-page-%s.aspx',      'pages': 35, 'cat': [14, 14]},  # дома пригород
    # аренда коммерческой недвижимости
    {'url': u'http://premier.ua/subcategory-20-page-%s.aspx',       'pages': 45, 'cat': [27, 27]},
    # продажа коммерческой недвижимости
    {'url': u'http://premier.ua/subcategory-31-page-%s.aspx',       'pages': 40, 'cat': [17, 17]},
    # клиенты
    {'url': u'http://premier.ua/subcategory-53-page-%s.aspx',       'pages': 11, 'cat': [100, 41]},  # сниму жилье
    {'url': u'http://premier.ua/subcategory-60-page-%s.aspx',       'pages': 10, 'cat': [100, 31]},  # куплю жилье
    {'url': u'http://premier.ua/subcategory-30-page-%s.aspx',       'pages': 2, 'cat': [100, 37]},  # куплю коммерческую
]

logging.basicConfig(level=logging.DEBUG)


def get_adv_on_page(grab=None):
    h3_urls = []
    for elem in grab.doc.select('//td[@class="adv-title"]/a'):
        h3_urls.append('http://premier.ua%s' % elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls


def get_adv_photo(grab):
    photo = []
    for img in grab.doc.select('//div[@class="adv-imgs"]/img'):
        tt = img.attr('src')
        tt = 'http://premier.ua%s' % tt
        photo.append(tt)
    photo = set(photo)
    return photo


def save_to_base(grab, task):
    try:
        slando = Slandos()

        title = grab.doc.select("//h2").text()
        region = grab.doc.select('//td')[9].text()
        phones = get_phone(grab, slando)
        text = grab.doc.select('//td[@colspan="2"]').text()
        cost = grab.doc.select('//td')[2].text()

        if title in text:
            text = text+region+phones
        else:
            if 'нет фото' != title:
                text = title+'. '+text+region+phones
            else:
                text = text+region+phones
        slando.cat = task.cat[0]
        slando.ci_cat = task.cat[1]
        slando.title = title
        slando.region = region
        slando.text = text
        slando.status = 0
        slando.date = datetime.datetime.now().strftime("%Y-%m-%d")
        slando.link = grab.response.url
        slando.cost = cost
        slando.site = 'premier.ua.final'
        slando.save()

        photo = get_adv_photo(grab)
        print slando.id
        print datetime.datetime.now().strftime("%Y-%m-%d: %H-%M")
        print 'task.cat', '==', task.cat[0], '=>', task.cat[0]
        print grab.response.url
        print phones.encode('utf-8'), u'----', cost.encode('utf-8'), u'----'

        return photo, slando, True
    except Exception, ex:
        print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)  # выводит строку(номер) ошибки
        print ex
        return False, False, False


def get_phone(grab, slando):
    phones = []
    for t, p in enumerate(grab.doc.select('//tr/td')):
        if p.text() == u'Телефон:':
            phone1 = str(parse_int(grab.doc.select('//tr/td')[t+1].text()))
            if phone1.isdigit() and phone1 != '0':
                phones.append(phone1)
                slando.phone1 = phone1
            phone2 = str(parse_int(grab.doc.select('//tr/td')[t+3].text()))
            if phone2.isdigit() and phone2 != '0':
                phones.append(phone2)
                slando.phone2 = phone2
    return ','.join(phones)


class SiteStructureParser(Spider):

    #setcategory
    def task_generator(self):
        grab = Grab()
        grab.load_proxylist(PROXY_PATH, 'text_file',
                            proxy_type='http', auto_init=False, auto_change=True)
        for link in VOCABULARY:
            url = link['url']
            pages = xrange(1, link['pages'])
            cat = link['cat']
            for page in pages:
                grab.change_proxy()
                grab.setup(
                    url=url % page,
                    proxy_userpwd=CREDENTIALS,
                    hammer_mode=True,
                    hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                    reuse_cookies=True
                )
                yield Task('link_on_page', grab=grab, cat=cat)

    # get adverton page
    def task_link_on_page(self, grab, task):
        print 'went'
        cat = task.cat
        print grab.doc.select('//title').text().encode('utf-8')
        grab.load_proxylist(PROXY_PATH,
                            'text_file',
                            proxy_type='http',
                            auto_init=False,
                            auto_change=True)
        for url in get_adv_on_page(grab):
            if up_date_for_fast_pars(url):
                continue
            grab.change_proxy()
            grab.setup(
                url=url,
                hammer_mode=True,
                hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                proxy_userpwd=CREDENTIALS,
                reuse_cookies=False
            )  # log_dir='vparser/tmp',
            yield Task('content', grab=grab, cat=cat)

    #get content
    def task_content(self, grab, task):
        photo, slando, status = save_to_base(grab, task)
        if status:
            if photo:
                for i, img in enumerate(photo):
                    print u'has sent to task - %s' % i
                    grab.setup(
                        url=img,
                        hammer_mode=True,
                        hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                        proxy_userpwd=CREDENTIALS,
                        reuse_cookies=True
                    )
                    yield Task('img', grab=grab, propr=slando, i=i)
        else:
            print 'REPEAT ---'
            grab.load_proxylist(PROXY_PATH, 'text_file',
                                proxy_type='http', auto_init=False, auto_change=True)
            grab.setup(
                url=grab.response.url,
                proxy_userpwd=CREDENTIALS,
                hammer_mode=True,
                hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                reuse_cookies=True
            )  # , log_dir='vparser/tmp'
            grab.change_proxy()
            yield Task('content', grab=grab, task_try_count=task.task_try_count + 1)

    def task_img(self, grab, task):
        grab.response.save(('%s/vparser/tmp/img/%s_%s.jpg' % (
            os.path.split(PROJECT_PATH)[0], task.propr.id, task.i)), create_dirs=False)
        print 'have to been save image - %s_%s' % (task.propr.id, task.i)
