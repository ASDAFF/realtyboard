# -*- coding: utf-8 -*-
import datetime, json, logging, os, re, sys
from django.utils.timezone import utc
from fake_useragent import UserAgent
from grab import Grab
from grab.spider import Spider, Task
from importdb.models import Slandos
from vparser.utils import CREDENTIALS, up_date_for_fast_pars, moder_phone, PROXY_PATH
from vparser.utils import parse_int

from realtyboard.settings import PROJECT_PATH

OTHER_TEMPLATE = [
    '2436644',
    '2436641',
    '2436650',
    '2436662'
]

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

VOCABULARY = [  # voc in list
    {'url': 'http://kharkovestate.com/arenda?page=%s',      'pages': 6, 'cat': [21, 21]},  # other template
    {'url': 'http://kharkovestate.com/posutochno?page=%s',      'pages': 6, 'cat': [21, 21]},  # other template
    # {'url': 'http://kharkovestate.com/search/2436650?page=%s',      'pages': 3, 'cat': [21, 24]},  # other template
    {'url': 'http://kharkovestate.com/sell-apt?page=%s',      'pages': 9, 'cat': [11, 11]},
    # {'url': 'http://kharkovestate.com/search/2436652?page=%s',      'pages': 3, 'cat': [11, 12]},
    {'url': 'http://kharkovestate.com/sell-house?page=%s',      'pages': 9, 'cat': [14, 14]},
    # {'url': 'http://kharkovestate.com/search/2436654?page=%s',      'pages': 9, 'cat': [14, 14]},
    # {'url': 'http://kharkovestate.com/search/2436658?page=%s',      'pages': 2, 'cat': [14, 14]},
    # {'url': 'http://kharkovestate.com/search/2436656?page=%s',      'pages': 7, 'cat': [14, 16]},
    # {'url': 'http://kharkovestate.com/search/2436662?page=%s',      'pages': 6, 'cat': [27, 27]},  # other template
    # {'url': 'http://kharkovestate.com/search/2436660?page=%s',      'pages': 9, 'cat': [17, 17]},
    {'url': 'http://kharkovestate.com/buy?page=%s',      'pages': 9, 'cat': [100, 100]},
    {'url': 'http://kharkovestate.com/rent?page=%s',      'pages': 9, 'cat': [100, 100]},

]


def save_to_base(grab, task, g2):
    try:
        title = grab.doc.select('//h1').text()
        text = grab.doc.select('//div[@class="objava-text"]').text()
        cost = grab.doc.select('//td[@class="data-value"]')[1].text()
        room = grab.doc.select('//td[@class="data-value"]').text()
        deteil = grab.doc.select('//table[@class="estobjava-datasheet"]').text()
        phones = get_phone(grab)

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
            slando.site = 'khest.ua.final'

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
    return set([photo.attr('href') for photo in grab.doc.select('//ul[@class="imagegallery"]/li/a')])


def get_adv_on_page(grab):
    h3_urls = []

    # for elem in grab.doc.select('//h4/a'):
    #     h3_urls.append(elem.attr('href'))
    print grab.response.url
    ff = [x for x in OTHER_TEMPLATE if x in grab.response.url]
    print 'ff---------------------------------------', ff
    if not ff:
        # print 'first'
        # for elem in grab.doc.select('//h4/a'):
        #     print elem.attr('href')
        #     h3_urls.append(elem.attr('href'))
        # print 'res=', set([elem.attr('href') for elem in grab.doc.select('//div[@class="estobjava-list-title"]/a')])
        return set([elem.attr('href') for elem in grab.doc.select('//div[@class="estobjava-list-title"]/a')])
        # return set([elem.attr('href') for elem in grab.doc.select('//h4/a')])
    else:
        # print 'second'
        # for elem in grab.doc.select('//div[@class="estobjava-list-title"]/a'):
        #     h3_urls.append(elem.attr('href'))
        # print 'res2=', set([elem.attr('href') for elem in grab.doc.select('//h4/a')])
        return set([elem.attr('href') for elem in grab.doc.select('//h4/a')])
        # return set([elem.attr('href') for elem in grab.doc.select('//div[@class="estobjava-list-title"]/a')])
    print 'h3_urls', h3_urls
    return h3_urls


def get_phone(grab):
    return [phone.text() for phone in grab.doc.select('//ul/a[@class="phone"]')]


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
        # print grab.response.url
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


def test_khest():
    ua = UserAgent()
    grab = Grab(timeout=30, log_file='%s/vparser/tmp/pars/log.html' % os.path.split(PROJECT_PATH)[0])
    grab.setup(proxy='46.148.30.250:8080', proxy_type='http', proxy_userpwd=CREDENTIALS)  # , log_dir='vparser/tmp'
    grab.go('http://kharkov.kha.slando.ua/obyavlenie/sdam-gostinku-tsentr-vse-udobstva-ID75tep.html#13fed9ae6e;promoted')
    # grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')

    # ff = grab.doc.select('//div[@class="pricelabel tcenter"]')
    # print ff.text()
    # for f in get_adv_on_page(grab):
    #     print f
    # g.setup(cookies={u'domain': u'secure.e-konsulat.gov.pl', u'name':
    #                             u'MSZ', u'value': u'64e8734b-986c-4cd4-be44-b2c112ec49c8', u'expiry':
    #                                 '1362046140', u'path': u'/', u'secure': 'False'})
    # print get_adv_photo(grab)

    # for dd in grab.doc.select('//div[@class="pding5_10"]'):
    #     if dd.text().split(':')[0] == u'Количество комнат':
    #         print dd.text().split(':')[1]

    phones = get_phone(grab)

    # print len(phones)

    slando = Slandos()
    # for phone in phones:
    #     print phone
    moder_phone(phones, slando)
    # print len(phones)

    # print grab.doc.select('//title').text()
    # print 'cookies==', grab.response.cookies
    # for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
    #     print img.attr('src')