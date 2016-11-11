# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from django.utils import timezone
from grab import Grab
from grab.spider import Spider, Task
from importdb.models import *
import datetime
import shutil
import sys, os, re
from fake_useragent import UserAgent
from board.models import *
from time import time
from realtyboard.settings import MEDIA_ROOT, USD_UAH

proxy_dir = os.path.join(MEDIA_ROOT, 'proxy')
LOGIN = 'UA88061'
PASSWORD = 'eIGF81N7mG'
CREDENTIALS = LOGIN+':'+PASSWORD
PROXY_PATH = proxy_dir+'/proxy_http_auth.txt'
HTM = ((20, 30), (40, 60),(60, 80))

#box
LOGIN_box = 'UA94671'
PASSWORD_box = '9X93nZXQ7h'
CREDENTIALS_box = LOGIN_box+':'+PASSWORD_box
PROXY_PATH_box = proxy_dir + '/box_clear.txt'

#fine
LOGIN_fine = 'UA88061'
PASSWORD_fine = 'eIGF81N7mG'
CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
PROXY_PATH_fine = proxy_dir + '/fine_clear.txt'

#elite
LOGIN_elite = 'UA111496'
PASSWORD_elite = 'WgN0eYlxA4'
CREDENTIALS_elite = LOGIN_elite+':'+PASSWORD_elite
PROXY_PATH_elite = proxy_dir + '/elite_clear.txt'

# logging.basicConfig(level=logging.DEBUG)


def up_date_for_fast_pars(url):
    sl = Slandos.objects.filter(link=url).first()
    if sl:
        sl.date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")
        sl.save()
        print 'UPDATE////////////////////////////////////////////////////////////////BUFFER'
        return True
    return False


def up_date_for_fast_pars_all_cities(url, city, price=None):
    # if city.slug == 'kharkov':
    #     up_date_for_fast_pars(url)
    adv = Advert.objects.filter(link=url, city=city).first()
    if adv:
        if price:
            int_price = int(parse_int(price))
            if '$' in price:
                price_usd = int_price
                price_uah = int_price * USD_UAH
            else:
                price_uah = int_price
                price_usd = int_price/USD_UAH
            adv.price_uah = price_uah
            adv.price_usd = price_usd
        adv.date_of_update = timezone.now()
        adv.save()
        print 'UPDATE////////////////////////////////////////////////////////////////'
        return True
    return False

# logging.basicConfig(level=logging.DEBUG)


class ProxyCheker(Spider):

    def __init__(self, service_proxy=False, *args, **kwargs):
        self.proxy_file = service_proxy
        self.test_url = 'http://olx.ua'
        self.thread_number=4
        super(ProxyCheker, self).__init__(*args, **kwargs)


    def task_generator(self):
        # get_proxy_box()
        get_proxy_fineproxy()
        get_proxy_elite()
        if self.proxy_file == 'fine_for_premier':
            get_proxy_fineproxy_for_premier()
            self.test_url = 'http://premier.ua/'
            # self.test_url = 'http://ci.ua/'
        if self.proxy_file == 'elite_for_premier':
            get_proxy_elite_for_premier()
            self.test_url = 'http://premier.ua/'
        if self.proxy_file == 'hideme':
            get_proxy_hideme()
            self.test_url = 'http://premier.ua/'
        grab = Grab()
        ua = UserAgent()
        # clear or create file before start check new proxies

        file_clear_proxy = open(
            proxy_dir + '/%s_clear.txt' % self.proxy_file, 'w'
        )
        file_clear_proxy.close()
        file_dirty_proxy = open(
            proxy_dir + '/%s.txt' % self.proxy_file, 'r'
        )
        # HTM = ((10, 20))
        # HTM = ((20, 30), (40, 60),(60, 80))
        HTM = ((60, 80))
        for dirty in file_dirty_proxy:
            print dirty
            grab.setup(url=self.test_url,
                       # url='http://premier.ua/',
                       proxy=dirty,
                       proxy_type='http',
                       # proxy_type='socks5',
                       proxy_userpwd=CREDENTIALS,
                       hammer_mode=True,
                       timeout=100,
                       connect_timeout=100,
                       # hammer_timeouts=HTM,
                       user_agent=ua.random,
                       reuse_cookies=False)
            yield Task('check', delay=3, grab=grab)


    def task_check(self, grab, task):
        print 'it perhaps have been written'
        file_clear_proxy = open(
            proxy_dir + '/%s_clear.txt' % self.proxy_file, 'a'
        )
        file_clear_proxy.write(grab.config['proxy'])
        file_clear_proxy.close()


def get_proxy_fineproxy():
    grab_proxy = Grab()
    grab_proxy.go('http://account.fineproxy.org/api/getproxy/?format=txt&type=httpauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    # grab_proxy.go('http://account.fineproxy.org/api/getproxy/?format=txt&type=socksauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    grab_proxy.response.save(proxy_dir + '/proxy_http_auth.txt', create_dirs=False)
    grab_proxy.response.save(proxy_dir + '/fine.txt', create_dirs=True)


def get_proxy_fineproxy_for_premier():
    grab_proxy = Grab()
    grab_proxy.go('http://account.fineproxy.org/api/getproxy/?format=txt&type=httpauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    # grab_proxy.go('http://account.fineproxy.org/api/getproxy/?format=txt&type=socksauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    grab_proxy.response.save(proxy_dir + '/fine_for_premier.txt', create_dirs=True)


def get_proxy_box():
    LOGIN = 'UA94671'
    PASSWORD = '9X93nZXQ7h'
    grab_proxy = Grab()
    grab_proxy.go('http://billing.proxybox.su/api/getproxy/?format=txt&type=httpauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    grab_proxy.response.save(proxy_dir + '/proxy_box_http.txt', create_dirs=False)
    grab_proxy.response.save(proxy_dir + '/box.txt', create_dirs=True)


def get_proxy_elite():
    LOGIN = 'UA86454'
    PASSWORD = '4fvvcxSbqN'
    #fine
    LOGIN_fine = 'UA88061'
    PASSWORD_fine = 'eIGF81N7mG'
    CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
    grab_proxy = Grab()
    grab_proxy.setup(proxy='193.106.31.167:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)
    grab_proxy.go('http://billing.proxyelite.ru/api/getproxy/?format=txt&type=httpauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    grab_proxy.response.save(proxy_dir + '/proxy_elite_http.txt', create_dirs=False)
    grab_proxy.response.save(proxy_dir + '/elite.txt', create_dirs=True)


def get_proxy_elite_for_premier():
    LOGIN = 'UA86454'
    PASSWORD = '4fvvcxSbqN'
    #fine
    LOGIN_fine = 'UA88061'
    PASSWORD_fine = 'eIGF81N7mG'
    CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
    grab_proxy = Grab()
    grab_proxy.setup(proxy='193.106.31.167:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)
    grab_proxy.go('http://billing.proxyelite.ru/api/getproxy/?format=txt&type=httpauth&login=%s&password=%s' % (LOGIN, PASSWORD))
    grab_proxy.response.save(proxy_dir + '/elite_for_premier.txt', create_dirs=True)


def moder_phone(phones, slando):
    if len(phones) >= 1:
        slando.phone1 = parse_int(phones[0])
    if len(phones) >= 2:
        slando.phone2 = parse_int(phones[1])
    if len(phones) >= 3:
        slando.phone3 = parse_int(phones[2])
    return ', 0'.join(phones)


def parse_int(string):
    string = string.encode('utf-8')
    value = ''.join([x for x in str(string) if x.isdigit()])[-9:]
    return str(value if len(value) else 0)


def get_proxy_hideme():
    grab_proxy = Grab()
    grab_proxy.go('http://hideme.ru/api/proxylist.php?&out=plain&type=h&maxtime=2000&code=865241682')
    file_proxy = open(proxy_dir + '/hideme.txt', 'w')
    file_proxy.write(grab_proxy.response.body)
    file_proxy.close()

    """""
    pass
    pytesser
    img_obg = StringIO(grab.response.body)
    image_to_string(Image.open(img_obg))
    from vparser.pytesser.pytesser import *
    from cStringIO import StringIO
    """""


def save_to_main_base(num_city=False,
                      text=False,
                      title=False,
                      category=False,
                      raw_phones=False,
                      cost=False,
                      link=False,
                      locality=False,
                      region=False,
                      room = False,
                      object_type = False,
                      living_area=False,
                      living_area_house=False,
                      floor=False):
    one_month = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=30)  # two days ago
    user_id = UserData.objects.get(id=8606)
    """
    it's may be importent
    # path_tmp = 'vparser/tmp/img/%s_%s.jpg' % (advert.id, '0')
    """
    piece = text[12:100].encode('utf-8')
    adv = Advert.objects.filter(author=user_id,
                                city=num_city, 
                                category=category,
                                phone__phone = int(parse_int(raw_phones.split(',')[0])),
                                main_text__contains=piece).first()
    int_price = int(parse_int(cost))
    if ('$' in cost):
        price_usd = int_price
        price_uah = int_price * USD_UAH
    else:
        price_uah = int_price
        price_usd = int_price / USD_UAH
    if adv:
        adv.date_of_update = timezone.now()
        # ad price update
        adv.price_usd = price_usd
        adv.price_uah = price_uah
        if adv.link:
            adv.link = link
        print u'UPDATE$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$','adv.id=', adv.id
        adv.save()
        return False
    else:
        board = Advert()
        board.title = title[:89]
        board.author = user_id
        board.category = category
        board.city = num_city
        board.price_unit = '1'
        board.main_text = text
        board.raw_phones = str(raw_phones)
        board.price_uah = price_uah
        board.price_usd = price_usd
        board.link = link
        board.site = locality
        board.seller = None
        if num_city.slug == 'kharkov':
            board.sublocality = board.detect_sublocality()
        if num_city.slug == 'kiev':
            board.big_sublocality = region if region else None
        board.save()

        if not hasattr(board, 'extraflat'):
            board.extraflat = ExtraFlat()
        if not hasattr(board, 'extrarent'):
            board.extrarent = ExtraRent()
        if not hasattr(board, 'extrahouse'):
            board.extrahouse = ExtraHouse()
        if room:
            # if connect type is one_to_one
            board.extraflat.rooms_number=int(parse_int(room))
            board.extraflat.save()
        if object_type:
            # if connect type is one_to_one
            board.extrarent.term = int(object_type)
            board.extrarent.save()
        if living_area:
            # if connect type is one_to_one
            board.extraflat.total_area=int(parse_int(living_area))
            board.extraflat.save()
        if floor:
            # if connect type is one_to_one
            board.extraflat.floor=int(parse_int(floor))
            board.extraflat.save()
        if living_area_house:
            # if connect type is one_to_one
            board.extrahouse.total_area=int(parse_int(living_area_house))
            board.extrahouse.save()
        
        print u'WRITE ADWERT $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$','board.id=', board.id
        return board
    # user_id.phone_set.clear()

def move_photo(board, id_proring):
    for i in xrange(0, 15):
        try:
            print 'board.id = ', board.id
            photo_id = Advert.objects.get(id=board.id)
            name = '%s_%s.jpg' % (id_proring, i)
            path_tmp = '%s/parser_temp_images/%s_%s.jpg' % (MEDIA_ROOT, id_proring, i)
            media_folder = os.path.join(settings.MEDIA_ROOT, name[:2])

            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            media = os.path.join(settings.MEDIA_ROOT, name[:2], name)

            if photo_id and os.path.isfile(path_tmp):
                shutil.copy(path_tmp, media)
                ph = "%s/%s" % (name[:2], name)
                Photo.objects.get_or_create(
                    advert=photo_id,
                    photo=ph)
        except Exception, ex:
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
            print ex

def save_to_buffer(grab, task, phones, category, moroz=False):
    try:
        title = grab.doc.select('//h1').text()
        text = grab.doc.select('//div[@id="textContent"]').text()
        cost = grab.doc.select('//div[@class="pricelabel tcenter"]').text()
        deteil = grab.doc.select('//table[@class="details fixed marginbott20 margintop5"]').text()
        room = ''
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Количество комнат':
                room = dd.text().split(':')[1]
            elif dd.text().split(':')[0] == u'Всего комнат в квартире':
                room = dd.text().split(':')[1]

        if phones:
            slando = Slandos()
            phones = phones.split(',')

            if len(phones) >= 1:
                slando.phone1 = parse_int(phones[0])
            if len(phones) >= 2:
                slando.phone2 = parse_int(phones[1])
            if len(phones) >= 3:
                slando.phone3 = parse_int(phones[2])

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
            slando.cat = task.moroz
            slando.ci_cat = category.id
            slando.date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")
            slando.site = 'slando.ua.final_trough_anoter'

            slando.save()

    except Exception, ex:
        print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)  # выводит строку(номер) ошибки
        print ex
        print 'something wrong with buffer'


class CustomizationForParser(Spider):

    def __init__(self, service_proxy=False, city_pars=False, moroz=False, *args, **kwargs):
        self.city_pars = city_pars
        self.moroz = moroz
        self.proxy_file = service_proxy
        self.proxy_file = service_proxy
        self.cat = False
        self.board = False
        self.i = False
        self.city = False
        self.room = False
        self.cost_uah = False

        if self.proxy_file == 'fine':
            self.CREDENTIALS = CREDENTIALS_fine
            self.PROXY_PATH =  PROXY_PATH_fine
        if self.proxy_file == 'box':
            self.CREDENTIALS = CREDENTIALS_box
            self.PROXY_PATH =  PROXY_PATH_box
        if self.proxy_file == 'elite':
            self.CREDENTIALS = CREDENTIALS_elite
            self.PROXY_PATH =  PROXY_PATH_elite
            # site = ProxyCheker(thread_number=500, network_try_limit=1, service_proxy=self.proxy_file)
            # site.run()
        if self.proxy_file == 'hideme':
            self.PROXY_PATH_hideme = proxy_dir + '/hideme_clear.txt'
        super(CustomizationForParser, self).__init__(*args, **kwargs)


def remove_portal_from_title():
    ads = Advert.objects.filter(title__contains=u"Рекламно-и")
    print ads.count()
    for ad in ads:
        ad.title = re.sub(ur'Рекламно-и.*', '', ad.title)
        if ad.sublocality_id == 2284:
            ad.sublocality_id = ad.detect_sublocality()
        ad.save()