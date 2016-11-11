# -*- coding: utf-8 -*-
import datetime, json, logging, os, re, sys
from django.utils.image import _detect_image_library
from django.utils.timezone import utc
from fake_useragent import UserAgent
from grab import Grab
from grab.selector import Selector
from grab.spider import Spider, Task
from lxml.html import fromstring
from vparser.utils import CREDENTIALS, up_date_for_fast_pars, moder_phone, PROXY_PATH

from board.utils import parse_int
from importdb.models import Slandos
from realtyboard.settings import PROJECT_PATH

logging.basicConfig()
# logging.basicConfig(level=logging.DEBUG)

VOCABULARY = [
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-kvartiru/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',       'pages': 20, 'cat': [21, 21]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-dom/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',            'pages': 2,  'cat': [21, 24]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-komnatu/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',        'pages': 2,  'cat': [21, 22]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-kvartiru/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',       'pages': 20, 'cat': [11, 11]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-komnatu/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',        'pages': 20, 'cat': [11, 12]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-dachu/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',          'pages': 2, 'cat': [14, 14]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-zemelnyj-uchastok-dlja-stroitelstva-zhilja/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',          'pages': 3, 'cat': [14, 16]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-obshchepit/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',     'pages': 3, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-dlja-industrii/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s', 'pages': 2, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-sklad/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-torgovoe-pomeshhenie/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-pomeshhenie-svobodnogo-naznachenija/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/snjat-gotovyj-biznes/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [27, 27]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-gotovyj-biznes/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-ofis/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-dlja-industrii/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-sklad/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-torgovoe-pomeshhenie/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-pomeshhenie-svobodnogo-naznachenija/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-zdanie/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-garazh/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    {'url': u'http://harkov.est.ua/nedvizhimost/kupit-gotovyj-biznes/?submitted=1&price_currency=uah&apps-theme=gallery&p=%s',           'pages': 2, 'cat': [17, 17]},
    # {'url': u'http://harkov.est.ua/nedvizhimost/snjat-kvartiru/?submitted=1&price_currency=usd/?page=%s',       'pages': 5, 'cat': 21},
    # {'url': u'http://harkov.est.ua/nedvizhimost/snjat-posutochno-dom/?submitted=1&price_currency=usd/?page=%s', 'pages': 6, 'cat': 21},
    # {'url': u'http://harkov.est.ua/nedvizhimost/kupit-kvartiru/?submitted=1&price_currency=usd/?page=%s',       'pages': 4, 'cat': 11},
]


def get_adv_on_page(grab=None):
    h3_urls = []
    for elem in grab.doc.select('//div[@class="eo-gallery-item-title"]/a'):
        h3_urls.append(elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls


def save_to_base(grab, task):
    try:
        slando = Slandos()
        title = grab.doc.select("//h1").text()
        if grab.doc.select('//div[@class="promo promo-richtext"]').exists():
            text = grab.doc.select('//div[@class="promo promo-richtext"]').text()
        else:
            text = grab.doc.select('//div[@class="promo"]').text()

        deteil = []
        room = ''

        for det in grab.doc.select('//tr'):
            deteil.append(det.text())
            root = Selector(fromstring(det.html()))
            if root.select('//tr/th').exists():
                if root.select('//tr/th').text() == u'Количество комнат':
                    room = root.select('//tr/td').text()
                if root.select('//tr/th').text() == u'Телефон':
                    phones = root.select('//tr/td').text().split('+')[1:]
        deteil = ', '.join(deteil)

        raw_phones = moder_phone(phones, slando)
        cost = grab.doc.select('//div[@class="app-price-line"]/span[@class="app-price"]').text()
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
        slando.site = 'est.ua.final'

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
    grab.response.unicode_body('utf-8')
    for img in grab.doc.select('//ul[@class="slideshow-slides"]/li/div/img'):
        tt = img.html()
        hh = re.findall(r'data-src="(.*?)"', tt.encode('utf-8'))
        if len(hh):
            # print hh[0]
            photo.append(hh[0])
    photo = set(photo)
    return photo


class SiteStructureParser(Spider):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab(timeout=30)
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
                    hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                    user_agent=ua.random,
                    reuse_cookies=False
                )
                yield Task('link_on_page', grab=grab, cat=cat)

    # take all links on page
    def task_link_on_page(self, grab, task):
        ua = UserAgent()
        title = grab.doc.select('//title').text()
        print 'main title ===', title.encode('utf-8')
        print grab.response.url
        h3_urls = get_adv_on_page(grab)
        print h3_urls
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
                    hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                    proxy_userpwd=CREDENTIALS,
                    user_agent=ua.random,
                    reuse_cookies=True)  # log_dir='vparser/tmp', reuse_cookies=True
                yield Task('content', grab=grab, cat=task.cat)

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
                hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                user_agent=ua.random,
                reuse_cookies=True
                # , log_dir='vparser/tmp'
            )
            grab.change_proxy()
            yield Task('content', grab=grab, task_try_count=task.task_try_count + 1)

    def task_img(self, grab, task):
        grab.response.save(('%s/vparser/tmp/img/%s_%s.jpg' % (
            os.path.split(PROJECT_PATH)[0], task.propr.id, task.i)), create_dirs=False)
        print 'have to been save image - %s_%s' % (task.propr.id, task.i)
