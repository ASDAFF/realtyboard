# -*- coding: utf-8 -*-
import datetime, json, logging, os, re, time
from django.core.files.base import ContentFile
from django.utils.timezone import utc
from fake_useragent import UserAgent
from grab import Grab
from grab.spider import Spider, Task
from hashlib import md5
from vparser.utils import parse_int
from vparser.utils import HTM, save_to_main_base, up_date_for_fast_pars_all_cities
from vparser.utils import CustomizationForParser, ProxyCheker, save_to_buffer #,test_slando_proxy #CREDENTIALS, PROXY_PATH,

from board.models import City, Category, BigSublocality, Photo
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
    'kiev'   :[[u'http://dom.ria.com/ru/Каталог',u'Киевская', u'Киев'],      8],
    'kharkov':[[u'http://dom.ria.com/ru/Каталог',u'Харьковская', u'Харьков'], 20]
}


VOCABULARY = [
    {'url': u'%s/Аренда-Помесячно/Квартиры/Область/%s/Город/%s/?page=%s',      'pages': 10, 'cat': [21, 21]},
    {'url': u'%s/Аренда-Помесячно/Дома/Область/%s/Город/%s/?page=%s',          'pages': 10, 'cat': [21, 24]},
    {'url': u'%s/Продажа/Квартиры/Область/%s/Город/%s/?page=%s',               'pages': 10, 'cat': [11, 11]},
    {'url': u'%s/Продажа/Дома/Область/%s/Город/%s/?page=%s',                   'pages': 10, 'cat': [14, 14]},
    {'url': u'%s/Продажа/Участки/Область/%s/Город/%s/?page=%s',                'pages': 10, 'cat': [14, 16]},
    {'url': u'%s/Продажа/Коммерческая/Область/%s/Город/%s//?page=%s',          'pages': 10, 'cat': [27, 27]},
    {'url': u'%s/Аренда-Помесячно/Коммерческая/Область/%s/Город/%s/?page=%s',  'pages': 10, 'cat': [17, 17]}
]



def save_to_base(grab, task, g2):
    # try:

    def type_rent():
        return 2 if task.cat.id == 21 else 1

    def region(city):
        try:
            region = grab.doc.select("//h1").text().split(',')[3].encode('utf-8').replace(' р-н. ', '')
            city_obj = City.objects.get(id=city.id)
            bs = BigSublocality.objects.filter(city=city_obj, name__contains=region).first()
            if bs:
                return bs
            else:
                return False
        except Exception, ex:
            print ex
            return False
    def room():
        if task.cat.id == 14:
            room = None
        else:
            room = grab.doc.select('//p[@class="item-param"]')[2].text()

    def text():
        if grab.doc.select('//div[@class="box-panel rocon description-view"]').exists():
            text = grab.doc.select('//div[@class="box-panel rocon description-view"]').text()
        else:
            deteil = []
            for det in grab.doc.select('//p[@class="item-param"]')[:5]:
                deteil.append(det.text())
            text = ','.join(deteil)
        return text
    print grab.response.url
    title = grab.doc.select("//h1").text()
    text = text()
    cost = grab.doc.select('//div[@class="price-seller"]').text()
    region_obj = region(task.city)

    phones = []
    for phone in grab.doc.select('//div[@class="item-param"]/strong[@class="phone"]'):
        phones.append(phone.text())

    phones = ','.join(phones)


    room_tot = room()
    rent = type_rent()

    print 'title = ', title.encode('utf-8')
    print 'text = ', text.encode('utf-8')
    print 'cost = ', cost.encode('utf-8')
    print 'phones = ', phones
    print 'region = ', region_obj
    if room_tot:
        print 'room = ', room_tot.encode('utf-8')
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
            print 'Advert.id = ', board.id
            photo = get_adv_photo(grab)
        return photo, board, True



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

def get_adv_on_page(grab=None):
    h3_urls = []
    for elem in grab.doc.select('//span[@class="city"]/a'):
        h3_urls.append('http://dom.ria.com%s' % elem.attr('href'))
    h3_urls = set(h3_urls)
    return h3_urls

def get_phone(grab):
    #return str
    pass


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
            part_url = LOCALITY[self.city_pars]
            pages = xrange(1, link['pages'])
            cat = Category.objects.get(id=link['cat'][1])
            moroz = link['cat'][0]
            city = City.objects.get(id=LOCALITY[self.city_pars][1])
            for page in pages:
                print 'number_of_pages=', page
                grab.change_proxy()
                grab.setup(
                    url=url % (part_url[0][0], part_url[0][1], part_url[0][2], page),
                    proxy_userpwd=self.CREDENTIALS,
                    hammer_mode=True,
                    hammer_timeouts=HTM,
                    user_agent=ua.random,
                    reuse_cookies=False
                )
                # check_proxies_for_slando(self, grab=grab, ua=ua.random, url=url % (LOCALITY[self.city_pars][0], page))
                print 'proxy before go of page list ', grab.config['proxy']
                yield Task('link_on_page', delay=4, grab=grab, cat=cat, city=city, moroz=moroz)


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
                yield Task('content', delay=4, grab=grab, cat=task.cat, city=task.city, moroz=task.moroz)

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
                    yield Task('img', delay=4, grab=grab, board=board, i=i, cat=task.cat, city=task.city, moroz=task.moroz)
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



def test_domria():

    ua = UserAgent()
    grab = Grab(timeout=30, 
                connect_timeout =10,  
                log_file='%s/vparser/tmp/pars/log.html' % os.path.split(PROJECT_PATH)[0])
    grab.setup(proxy='46.148.30.216:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_box)  # , log_dir='vparser/tmp'
    # grab.go('http://kiev.ko.slando.ua/obyavlenie/predlagaetsya-v-arendu-posutochno-v-kieve-kvartira-odnokomnatnaya-po-ulits-ID75E19.html#a025724d26')
    grab.go('http://dom.ria.com/ru/realty_prodaja_dom_harkov_olhovka_stepnaya_ulitsa-8253714.html')
    # grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')


    print grab.doc.select('//div[@class="item-param"]/strong[@class="phone"]').text()


    # print grab.doc.select('//div[@class="price-seller"]').text()