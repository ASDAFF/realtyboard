# -*- coding: utf-8 -*-
from django.utils import timezone
from fake_useragent import UserAgent
from grab import Grab
from grab.spider import Spider, Task

from realtyboard.settings import MEDIA_ROOT
#fine
LOGIN_fine = 'UA88061'
PASSWORD_fine = 'eIGF81N7mG'
CREDENTIALS_fine = LOGIN_fine+':'+PASSWORD_fine
PROXY_PATH_fine = '%s/proxy/fine_clear.txt' % MEDIA_ROOT
HTM = ((20, 30), (40, 60),(60, 80))


def ria_test():
    grab = Grab()
    # grab.go(u'http://dom.ria.com/ru/Каталог/Продажа-аренда/')
    # print grab.doc.select('//a[@id="extended_search_link"]').text()
    # print grab.doc.select('//a[@class="photo photo-185x120"]').attr('href')
    # for item in grab.doc.select('//a[@class="photo photo-185x120"]'):
    #     print item.attr('href')
    grab.setup(proxy='46.148.30.250:8080', proxy_type='http', proxy_userpwd=CREDENTIALS_fine)  # , log_dir='vparser/tmp'        
    grab.go(u'http://dom.ria.com/ru/realty_prodaja_kvartira_harkov_kominternovskiy_pr_geroev_stalingrada-8904018.html')
    print grab.doc.select('//div[@class="box-panel rocon description-view"]/p').text()
    
    
class SiteStructureParser(Spider):
    def task_generator(self):
        ua = UserAgent()
        grab = Grab()
        grab.load_proxylist(
            PROXY_PATH_fine,
            'text_file',
            proxy_type='http',
            auto_init=False,
            auto_change=True
        )
        g =Grab()
        g.go(u'http://dom.ria.com/ru/Каталог/Продажа-аренда/')
        print 'sssssssssssssssssssssssssssss', g.doc.select('//a[@class="photo photo-185x120"]')
        for item in g.doc.select('//a[@class="photo photo-185x120"]'):
            print u'http://dom.ria.com/%s' % item.attr('href')
            grab.setup(
                url=u'http://dom.ria.com%s' % item.attr('href'),
                proxy_userpwd=CREDENTIALS_fine,
                hammer_mode=True,
                hammer_timeouts=HTM,
                user_agent=ua.random,
                reuse_cookies=False
            )
            yield Task('link_on_page', grab=grab)
    
    def task_link_on_page(self, grab, task):
        print 'jdhgjsdbhc'            
        print grab.doc.select('//div[@class="box-panel rocon description-view"]/p').text()