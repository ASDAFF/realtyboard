# -*- coding: utf-8 -*-
import datetime, logging, os, re, sys
from django.utils.timezone import utc
from fake_useragent import UserAgent
from grab import Grab
from grab.spider import Spider, Task
from importdb.models import Slandos
from vparser.utils import parse_int
from vparser.utils import CREDENTIALS, up_date_for_fast_pars, moder_phone, PROXY_PATH

from realtyboard.settings import PROJECT_PATH

VOCABULARY = [
    {'url': u'http://dom.ria.com/ru/Каталог/Аренда-Помесячно/Квартиры/Область/Харьковская/Город/Харьков/?page=%s',      'pages': 30, 'cat': [21, 21]},
    {'url': u'http://dom.ria.com/ru/Каталог/Аренда-Помесячно/Дома/Область/Харьковская/Город/Харьков/?page=%s',          'pages': 30, 'cat': [21, 24]},
    {'url': u'http://dom.ria.com/ru/Каталог/Продажа/Квартиры/Область/Харьковская/Город/Харьков/?page=%s',               'pages': 30, 'cat': [11, 11]},
    {'url': u'http://dom.ria.com/ru/Каталог/Продажа/Дома/Область/Харьковская/Город/Харьков/?page=%s',                   'pages': 30, 'cat': [14, 14]},
    {'url': u'http://dom.ria.com/ru/Каталог/Продажа/Участки/Область/Харьковская/Город/Харьков/?page=%s',                'pages': 30, 'cat': [14, 16]},
    {'url': u'http://dom.ria.com/ru/Каталог/Продажа/Коммерческая/Область/Харьковская/Город/Харьков//?page=%s',          'pages': 30, 'cat': [27, 27]},
    {'url': u'http://dom.ria.com/ru/Каталог/Аренда-Помесячно/Коммерческая/Область/Харьковская/Город/Харьков/?page=%s',  'pages': 30, 'cat': [17, 17]}
]

logging.basicConfig()
# logging.basicConfig(level=logging.DEBUG)


def get_adv_on_page(grab=None):
    h3_urls = []
    for elem in grab.doc.select('//span[@class="city"]/a'):
        h3_urls.append('http://dom.ria.com%s' % elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls


def get_adv_photo(grab):
    photo = []
    for img in grab.doc.select('//div[@class="wrapper"]/a'):
        tt = img.attr('onclick')
        hh = re.findall(r'\'dom/photo/(.*?)\'', tt.encode('utf-8'))
        if len(hh):
            full_link = 'http://cdn.img.ria.com/photos/dom/photo/%s' % (hh[0])
            full_link = full_link.replace('.jpg', 'f.jpg')
            photo.append(full_link)
    photo = set(photo)
    return photo


def save_to_base(grab, task):

    try:
        slando = Slandos()
        print grab.response.url
        title = grab.doc.select("//h1").text()

        if grab.doc.select('//div[@class="box-panel rocon description-view"]').exists():
            text = grab.doc.select('//div[@class="box-panel rocon description-view"]').text()
        else:
            deteil = []
            for det in grab.doc.select('//p[@class="item-param"]')[:5]:
                deteil.append(det.text())
            text = ','.join(deteil)

        if task.cat == 14:
            room = ''
        else:
            room = grab.doc.select('//p[@class="item-param"]')[2].text()

        cost = grab.doc.select('//div[@class="price-seller"]').text()

        phones = []
        for phone in grab.doc.select('//div[@class="item-param"]/strong[@class="phone"]'):
            phones.append(phone.text())

        raw_phones = moder_phone(phones, slando)

        if title in text:
            text = text+room+'  '+raw_phones.decode('utf-8')+'  '+cost
        else:
            text = title+'. '+text+room+'  '+raw_phones.decode('utf-8')+'  '+cost

            slando.title = title
            slando.text = text
            slando.cost = cost
            slando.room = room
            slando.status = 0
            slando.link = grab.response.url
            slando.cat = task.cat[0]
            slando.ci_cat = task.cat[1]
            slando.date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")
            slando.site = 'dom.ria.com.final'

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
