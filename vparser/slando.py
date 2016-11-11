# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from grab import Grab
from fake_useragent import UserAgent
import re
from grab.spider import Spider, Task
from vparser.utils import CREDENTIALS, up_date_for_fast_pars, moder_phone, HTM, PROXY_PATH
from vparser.utils import parse_int
import logging
import json
from importdb.models import Slandos
import datetime
import sys, os
from realtyboard.settings import MEDIA_ROOT

from realtyboard.settings import PROJECT_PATH

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

VOCABULARY = [  # voc in list
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/?page=%s',       'pages': 10, 'cat': [21, 21]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-komnat/?page=%s',        'pages': 10, 'cat': [21, 22]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-domov/?page=%s',         'pages': 10, 'cat': [21, 24]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-kvartir/?page=%s',     'pages': 10, 'cat': [11, 11]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-komnat/?page=%s',      'pages': 10, 'cat': [11, 12]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-domov/?page=%s',       'pages': 10, 'cat': [14, 14]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-zemli/?page=%s',       'pages': 10, 'cat': [14, 16]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-pomescheniy/?page=%s',   'pages': 10, 'cat': [27, 27]},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-pomescheniy/?page=%s', 'pages': 10, 'cat': [17, 17]},
]


def save_to_base(grab, task, g2):
    try:
        title = grab.doc.select('//h1').text()
        text = grab.doc.select('//div[@id="textContent"]').text()
        cost = grab.doc.select('//div[@class="pricelabel tcenter"]').text()
        deteil = grab.doc.select('//table[@class="details fixed marginbott20 margintop5"]').text()
        phones = get_phone(g2)
        room = ''
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Количество комнат':
                room = dd.text().split(':')[1]
            elif dd.text().split(':')[0] == u'Всего комнат в квартире':
                room = dd.text().split(':')[1]

        if phones:
            slando = Slandos()
            raw_phones = moder_phone(phones, slando)
            if title in text:
                text = text+deteil+room+'  '+raw_phones.decode('utf-8')+'  '+cost
            else:
                text = title+'. '+text+deteil+room+'  '+raw_phones.decode('utf-8')+'  '+cost

            slando.title = title
            slando.text = text
            slando.cost = cost
            slando.room = room
            slando.status = 0
            slando.link = grab.response.url
            slando.cat = task.cat[0]
            slando.ci_cat = task.cat[1]
            slando.date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")
            slando.site = 'slando.ua.final'

            photo = get_adv_photo(grab)

            slando.save()
            print slando.id
            print datetime.datetime.now().strftime("%Y-%m-%d: %H-%M")
            # print 'task.cat', '==', task.cat[0], '=>', task.cat[0]
            print grab.response.url
            print raw_phones.encode('utf-8'), u'----', cost.encode('utf-8'), u'----', room.encode('utf-8')
            return photo, slando, True
    except Exception, ex:
        print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)  # выводит строку(номер) ошибки
        print ex
        return False, False, False


def get_adv_photo(grab):
    photo = []
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
    ajax_sl = "http://kharkov.kha.slando.ua/ajax/misc/contact/phone/%s/"\
              % (re.findall(r'-ID(.*?).html', grab.response.url)[0])
    grab.go(ajax_sl)
    json_mas = json.loads(grab.response.unicode_body('utf-8'))
    phones = []
    phones.append(json_mas['value'])
    if 'span' in json_mas['value']:
        phones = re.findall(r'">(.*?)</', json_mas['value'])

    check_phone = ' '.join(phones)

    if not 'img' in check_phone:
        return phones
    else:
        return False


class SiteStructureParser(Spider):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab()
        grab.load_proxylist(
            PROXY_PATH,
            'text_file',
            proxy_type='http',
            auto_init=False,
            auto_change=True
        )
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
                    hammer_timeouts=HTM,
                    user_agent=ua.random,
                    reuse_cookies=False
                )
                yield Task('link_on_page', grab=grab, cat=cat)

    # take all links on page
    def task_link_on_page(self, grab, task):
        ua = UserAgent()
        title = grab.doc.select('//title').text()
        print 'main title ===', title.encode('utf-8')
        h3_urls = get_adv_on_page(grab)
        if len(h3_urls):
            grab.load_proxylist(
                PROXY_PATH,
                'text_file',
                proxy_type='http',
                auto_init=False, auto_change=True
            )
            for url in h3_urls:
                if up_date_for_fast_pars(url):
                    continue
                grab.change_proxy()
                grab.setup(
                    url=url,
                    hammer_mode=True,
                    hammer_timeouts=HTM,
                    proxy_userpwd=CREDENTIALS,
                    user_agent=ua.random,
                    reuse_cookies=True)  # log_dir='vparser/tmp', reuse_cookies=True
                yield Task('content', grab=grab, cat=task.cat)

    #grab content
    def task_content(self, grab, task):
        g2 = grab.clone()
        photo, slando, status = save_to_base(grab, task, g2)
        if status:
            if photo:
                for i, img in enumerate(photo):
                    print u'has sent to task - %s' % i
                    grab.setup(
                        url=img,
                        hammer_mode=True,
                        hammer_timeouts=HTM,
                        proxy_userpwd=CREDENTIALS,
                        reuse_cookies=True
                    )
                    yield Task('img', grab=grab, propr=slando, i=i)
        else:
            print 'REPEAT----------------------'
            ua = UserAgent()
            grab.load_proxylist(
                PROXY_PATH,
                'text_file',
                proxy_type='http',
                auto_init=False,
                auto_change=True
            )
            grab.setup(
                url=grab.response.url,
                proxy_userpwd=CREDENTIALS,
                hammer_mode=True,
                hammer_timeouts=HTM,
                user_agent=ua.random,
                reuse_cookies=True
                # , log_dir='vparser/tmp'
            )
            grab.change_proxy()
            yield Task('content', grab=grab, task_try_count=task.task_try_count + 1)

    def task_img(self, grab, task):
        grab.response.save(('%s/parser_temp_images/%s_%s.jpg' % (MEDIA_ROOT, task.propr.id, task.i)),
                           create_dirs=False)
        print 'have to been save image - %s_%s' % (task.propr.id, task.i)


def test_slandos():
    ua = UserAgent()
    grab = Grab(timeout=30, 
                connect_timeout =10,  
                log_file='%s/vparser/tmp/pars/log.html' % os.path.split(PROJECT_PATH)[0])
    grab.setup(proxy='46.148.30.250:8080', proxy_type='http', proxy_userpwd=CREDENTIALS)  # , log_dir='vparser/tmp'
    grab.go('http://kharkov.kha.slando.ua/obyavlenie/prodam-otdelno-stoyaschee-zdanie-ID8qXHW.html#8ed021c837')
    # grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')

    # ff = grab.doc.select('//div[@class="pricelabel tcenter"]')
    # print ff.text()
    # for f in get_adv_on_page(grab):
    #     print f
    # g.setup(cookies={u'domain': u'secure.e-konsulat.gov.pl', u'name':
    #                             u'MSZ', u'value': u'64e8734b-986c-4cd4-be44-b2c112ec49c8', u'expiry':
    #                                 '1362046140', u'path': u'/', u'secure': 'False'})
    print get_adv_photo(grab)

    # for dd in grab.doc.select('//div[@class="pding5_10"]'):
    #     if dd.text().split(':')[0] == u'Количество комнат':
    #         print dd.text().split(':')[1]

    phones = get_phone(grab)

    # print len(phones)
    if len(phones) >= 1:
        print parse_int(phones[0])
    if len(phones) >= 2:
        print parse_int(phones[1])
    if len(phones) >= 3:
        print parse_int(phones[2])
    print','.join(phones)
    # slando = Slandos()
    for phone in phones:
        print phone
    # moder_phone(phones, slando)
    # print len(phones)

    # print grab.doc.select('//title').text()
    # print 'cookies==', grab.response.cookies
    # for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
    #     print img.attr('src')