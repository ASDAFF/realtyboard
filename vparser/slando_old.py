# -*- coding: utf-8 -*-
from symbol import continue_stmt
from django.utils.timezone import utc
from grab import Grab
from fake_useragent import UserAgent
import re
from vparser.pytesser.pytesser import *
from cStringIO import StringIO
from grab.spider import Spider, Task
from board.utils import parse_int
import logging
import json
from importdb.models import Slandos
import datetime
import sys


LOGIN = 'UA88061'
PASSWORD = 'eIGF81N7mG'
CREDENTIALS = LOGIN+':'+PASSWORD


VOCABULARY = [
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/?page=%s',       'pages': 70, 'cat': 21},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-komnat/?page=%s',        'pages': 40, 'cat': 21},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-domov/?page=%s',         'pages': 20, 'cat': 21},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-kvartir/?page=%s',     'pages': 50, 'cat': 11},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-komnat/?page=%s',      'pages': 40, 'cat': 11},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-domov/?page=%s',       'pages': 20, 'cat': 14},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-zemli/?page=%s',       'pages': 50, 'cat': 14},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/arenda-pomescheniy/?page=%s',   'pages': 40, 'cat': 27},
    {'url': 'http://kharkov.kha.slando.ua/nedvizhimost/prodazha-pomescheniy/?page=%s', 'pages': 40, 'cat': 17},
]



# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig()
# logger = logging.getLogger(__name__)


def get_proxy_hideme():
    grab_proxy = Grab()
    # grab_proxy.go('http://hideme.ru/api/proxylist.php?country=UA&out=js&type=h&code=777707576')
    grab_proxy.go('http://hideme.ru/api/proxylist.php?&out=js&type=h&maxtime=800&code=777707576')
    proxy_mas = json.loads(grab_proxy.response.unicode_body('utf-8'))
    proxy = []
    file_proxy = open('realtyboard/static/proxy.txt', 'w')
    i = 0
    for pro_m in proxy_mas:
        i+=1
        try:
            proxy_list = pro_m['host']+':'+pro_m['port']
            grab_proxy.setup(proxy=proxy_list, proxy_type='http')
            grab_proxy.go('http://slando.ua/')
            if grab_proxy.search(u'Доска объявлений Slando: сайт бесплатных частных объявлений в Украине - купля/продажа б/у товаров на Slando.ua'):
                file_proxy.write(proxy_list+"\n")
                proxy.append(proxy_list)
        except Exception, ex:
            pass
            # logger.error(ex)
        if i == 15:
            break
    file_proxy.close()
    print 'len=', len(proxy)
    return proxy

import sys





def save_to_base(grab, task, title, text, deteil, phone, cost=False, room=False, save_url=False):
    if title:
        text = title+'. '+text+deteil+'  '+phone.decode('utf-8')
    else:
        text = text+deteil+'  '+phone.decode('utf-8')
    print 'type(text)=================', type(text)
    piece = text[12:40]
    adv = Slandos.objects.filter(text__contains=piece, link=save_url, cat=str(task.cat)).first()
    if not adv:
        print 'write!!!!!!!!!!!!!'
        propr = Slandos()
        propr.cat = task.cat
        propr.text = text
        propr.status = 0
        propr.date = datetime.datetime.now().strftime("%Y-%m-%d")
        propr.link = save_url
        try:
            propr.phone1 = parse_int(phone.split(',')[0])
        except IndexError, ex:
            print u"don't take phone1", ex
        try:
            propr.phone2 = parse_int(phone.split(',')[1])
        except IndexError, ex:
            print u"don't take phone2", ex
        try:
            propr.phone3 = parse_int(phone.split(',')[2])
        except IndexError, ex:
            print u"don't take phone3", ex
        if cost:
            propr.cost = cost
        if room:
            propr.room = room

        propr.site = 'slando.ua.test'
        propr.save()
        print u'Успешное сохранение в БД'
        return propr
    else:
        print u'НЕ нуждается в сохранении в БД'
        return None


def get_phone(grab, url):
    # print '1 get phone', grab.config["user_agent"]
    ajax_ex = "http://kharkov.kha.slando.ua/ajax/misc/contact/phone/%s/" % (re.findall(r'-ID(.*?).html', url)[0])
    # grab.go(ajax_ex, log_file='vparser/tmp/img/url%s.html'% (re.findall(r'-ID(.*?).html', url)[0]))
    grab.go(ajax_ex)
    img = grab.response.body.replace('\\', '')
    real_image_url = re.findall(r'<img[^>]*\ssrc="(.*?)"', img)[0]
    # grab.go(real_image_url, log_file='vparser/tmp/img/img%s.png'% (re.findall(r'-ID(.*?).html', url)[0]))
    grab.go(real_image_url)
    # print 'after all get phone', grab.config["user_agent"]
    img_obg = StringIO(grab.response.body)
    return image_to_string(Image.open(img_obg))





def get_adv_photo(grab):
    photo = []
    for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
        photo.append(img.attr('src'))
    photo = set(photo)
    return photo


class SiteStructureParser(Spider):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab(timeout=30)
        grab.load_proxylist('proxy_http_auth.txt', 'text_file',
                            proxy_type='http', auto_init=False, auto_change=True)
        # grab.config["thread_number"] = 40
        for link in VOCABULARY:
            url = link['url']
            pages = xrange(1, link['pages'])
            cat = link['cat']
            for page in pages:
                grab.change_proxy()
                grab.setup(url=url % page, proxy_userpwd=CREDENTIALS,
                           hammer_mode=True, hammer_timeouts=((2, 5), (10, 15), (20, 30)), user_agent=ua.random, reuse_cookies=True)
                yield Task('link_on_page', grab=grab, cat=cat)

    # take all links on page
    def task_link_on_page(self, grab, task):
        # print grab.config["user_agent"]
        ua = UserAgent()
        # print grab.response.cookies
        title = grab.doc.select('//title').text()
        print title
        h3_urls = get_adv_on_page(grab)
        if len(h3_urls):

            # grab = Grab(timeout=30) # - new
            grab.load_proxylist('proxy_http_auth.txt', 'text_file',
                                proxy_type='http', auto_init=False, auto_change=True)
            # grab.config["thread_number"] = 5
            for url in h3_urls:
                if up_date_for_fast_pars(url):
                    continue
                grab.change_proxy()
                # sleep(3)
                grab.setup(url=url, hammer_mode=True, hammer_timeouts=((2, 5), (10, 15), (20, 30)), proxy_userpwd=CREDENTIALS, user_agent=ua.random, reuse_cookies=True)  # log_dir='vparser/tmp',
                yield Task('content', grab=grab, cat=task.cat)

    #grab content
    def task_content(self, grab, task):

        save_url = grab.response.url
        try:
            print '********************', grab.response.url, '**********************************'
            # print 'before get phone', grab.config["user_agent"]
            # print grab.response.cookies
            print 'task.cat==', task.cat
            print grab.config['proxy']
            title = grab.doc.select('//h1').text()
            print title
            text = grab.doc.select('//div[@id="textContent"]').text()
            print text
            try:
                cost = grab.doc.select('//div[@class="pricelabel tcenter"]').text()
                print cost
            except Exception, ex:
                cost = None
                print 'some trobles with cost'
                print ex
            try:
                room = grab.doc.select('//div[@class="pding5_10"]/strong')[5].text()
                print 'room', room
            except Exception, ex:
                room = None
                print 'some trobles with numbers_of_room'
                print ex
            deteil = grab.doc.select('//table[@class="details fixed marginbott20 margintop5"]').text()
            print deteil
            photo = get_adv_photo(grab)
            print photo
            phone = get_phone(grab=grab, url=grab.response.url)
            print phone
            propr = save_to_base(grab, task, title, text, deteil, phone, cost, room, save_url)
            if photo and propr:
                for i, img in enumerate(photo):
                    print u'Отправлено в задание - %s' % i
                    grab.setup(url=img, hammer_mode=True, hammer_timeouts=((2, 5), (10, 15), (20, 30)), proxy_userpwd=CREDENTIALS, reuse_cookies=True)
                    yield Task('img', grab=grab, propr=propr, i=i)
            print '********************', 'END', '*********************************************************************'
        except Exception, ex:
            print 'ПОВТОР ---', ex
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
            ua = UserAgent()
            # grab = Grab(timeout=30)
            grab.load_proxylist('proxy_http_auth.txt', 'text_file',
                                proxy_type='http', auto_init=False, auto_change=True)
            grab.setup(url=save_url, proxy_userpwd=CREDENTIALS, hammer_mode=True, hammer_timeouts=((2, 5), (10, 15), (20, 30)), user_agent=ua.random, reuse_cookies=True) # , log_dir='vparser/tmp'
            grab.change_proxy()
            yield Task('content', grab=grab, task_try_count=task.task_try_count + 1)

    def task_img(self, grab, task):
        grab.response.save(('/data/python/estate-kharkov.ci.ua/vparser/tmp/img/%s_%s.jpg' % (task.propr.id, task.i)), create_dirs=False)
        print u'Должна быть сохранена картинка - %s_%s' % (task.propr.id, task.i)

def test_slandos():
    grab = Grab(timeout=30)
    # grab.load_proxylist('proxy_http_auth.txt', 'text_file',
    #                         proxy_type='http', auto_init=False, auto_change=True)
    grab.setup(proxy='46.148.30.250:8080', proxy_type='http', proxy_userpwd=CREDENTIALS)  # , log_dir='vparser/tmp'
    grab.go('http://kharkov.kha.slando.ua/obyavlenie/srochno-sdam-shikarnuyu-1-k-kv-s-evroremontom-na-alekseevke-pr-pobedy-ID5JM5D.html#c3e60e4ca5')
    # print get_adv_photo(grab)
    print get_phone(grab=grab, url=grab.response.url)
    # print grab.doc.select('//title').text()
    # print grab.response.cookies
    # for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
    #     print img.attr('src')


























    '''
document_help
http://hideme.ru/api/proxylist.php?country=UA&out=js&type=h&code=777707576
  print grab.doc.select('//div[@class="pricelabel tcenter"]').select('.//strong[@class="xxxx-large margintop7 block not-arranged"]').text()
    print grab.doc.select('//div[@class="pricelabel tcenter"]/strong[@class="xxxx-large margintop7 block not-arranged"]').text()




print g.doc.select('//div[contains(@class, "post")][2]')[0].select('.//div[@class="favs_count"]').number()
print g.doc.select('//div[contains(@class, "post")][2]')[0].select('.//div[@class="favs_count"]')[0].html()
g.setup(post={'textpoisk': '456'})
g.setup(debug=True)


    for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
        print img.attr('src')



#######################################################################
    # def task_1phone(self, grab, task):
    #     print '1referer',grab.config['referer']
    #     print grab.config['proxy']
    #     print grab.response.body
    #     img = grab.response.body.replace('\\', '')
    #     real_image_url = re.findall(r'<img[^>]*\ssrc="(.*?)"', img)[0]
    #     print real_image_url
    #     grab.setup(url = real_image_url)
    #     yield Task('2phone', grab=grab, task_try_count=task.task_try_count + 1)
    #
    # def task_2phone(self, grab, task):
    #     print '2referer', grab.config['referer']
    #     print grab.config['proxy']
    #     print 'last - --- - ', grab.response.url
    #     img_obg = StringIO(grab.response.body)
    #     print u'ТЕЛЕФОН=====', image_to_string(Image.open(img_obg))
#######################################################################
    '''
