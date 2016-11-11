# -*- coding: utf-8 -*-
from tempfile import _RandomNameSequence
from grab import Grab
from fake_useragent import UserAgent
from grab.spider import Spider, Task
from vparser.utils import CREDENTIALS
import random


class SiteStructureParser(Spider):
    # take needed page links
    def task_generator(self):
        ua = UserAgent()
        grab = Grab(timeout=30)
        grab.load_proxylist(
            'proxy_http_auth.txt',
            'text_file',
            proxy_type='http',
            auto_init=False,
            auto_change=True
        )
        while True:
            dig = random.randint(111, 999)
            grab.change_proxy()
            grab.setup(
                url='http://zipexpert.com.ua/catalog/?q=%s&s=' % dig,
                # url='http://good-service.com.ua/content/zapchasti-dlya-stiralnykh-mashin-v-kharkove-i-po-vsei-ukraine-optom-i-v-roznitsu',
                proxy_userpwd=CREDENTIALS,
                hammer_mode=True,
                hammer_timeouts=((2, 5), (10, 15), (20, 30)),
                user_agent=ua.random,
                reuse_cookies=False
            )
            yield Task('link_on_page', grab=grab)

    def task_link_on_page(self, grab, task):
        print grab.response.url
        title = grab.doc.select('//title').text()
        print 'main title ===', title
        # ua = UserAgent()
        # title = grab.doc.select('//title').text()
        # print 'main title ===', title
        # h3_urls = get_adv_on_page(grab)
        # if len(h3_urls):
        #     grab.load_proxylist(
        #         'proxy_http_auth.txt',
        #         'text_file',
        #         proxy_type='http',
        #         auto_init=False, auto_change=True
        #     )
        #     for url in h3_urls:
        #         if up_date_for_fast_pars(url):
        #             continue
        #         grab.change_proxy()
        #         grab.setup(
        #             url=url,
        #             hammer_mode=True,
        #             hammer_timeouts=((2, 5), (10, 15), (20, 30)),
        #             proxy_userpwd=CREDENTIALS,
        #             user_agent=ua.random,
        #             reuse_cookies=True)  # log_dir='vparser/tmp', reuse_cookies=True
        #         yield Task('content', grab=grab, cat=task.cat)