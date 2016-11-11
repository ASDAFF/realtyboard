# -*- coding: utf-8 -*-
from django.utils.timezone import utc
from grab import Grab
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


def test_site():

    ua = UserAgent()
    grab = Grab(timeout=30, connect_timeout =10,  log_file='/data/python/estate-kharkov.ci.ua/vparser/tmp/pars/log.html')
    grab.setup(proxy='46.148.30.123:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)  # , log_dir='vparser/tmp'
    # grab.go('http://kiev.ko.slando.ua/obyavlenie/predlagaetsya-v-arendu-posutochno-v-kieve-kvartira-odnokomnatnaya-po-ulits-ID75E19.html#a025724d26')
    # grab.go('http://kharkov.kha.olx.ua/obyavlenie/bystroe-vselenie-v-krasivuyu-2k-kvartiru-tsentr-poryadochnost-dokumenty-IDavIV3.html#a51e020528')
    grab.go('http://kharkov.kha.slando.ua/nedvizhimost/arenda-kvartir/')


    def get_adv_on_page(grab):
        h3_urls = []
        for elem in grab.doc.select(u'//table[@summary="Объявление"]'):
            h3_urls.append\
            (
                [
                    elem.select('.//h3').select('.//a').attr('href'),
                    parse_int(elem.select('.//strong').text())
                ]
            )
        return h3_urls
    print get_adv_on_page(grab)

    extra_info = ' '.join(grab.doc.select('//span[@class="show-map-link link gray cpointer"]').text().split(',')[1:])
    print extra_info

    def living_area():
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Жилая площадь':
                print dd.text().split(':')[1]
                return dd.text().split(':')[1]


    def living_area_house():
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Площадь дома':
                print dd.text().split(':')[1]
                return dd.text().split(':')[1]


    def floor():
        for dd in grab.doc.select('//div[@class="pding5_10"]'):
            if dd.text().split(':')[0] == u'Этаж':
                print dd.text().split(':')[1]
                return dd.text().split(':')[1]
    #
    # living_area()
    # living_area_house()
    # floor()


    # def get_adv_photo(grab):
    #     photo = []
    #     try:
    #         photo.append(grab.doc.select('//div[@class="photo-glow"]/div[@class="photo-handler rel inlblk"]/img').attr('src'))
    #     except:
    #         pass
    #     for img in grab.doc.select('//div[@class="tcenter img-item"]/div[@class="photo-glow"]/img'):
    #         photo.append(img.attr('src'))
    #     photo = set(photo)
    #     return photo
    #
    #
    #
    # print get_adv_photo(grab)