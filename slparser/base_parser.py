# -*- coding: utf-8 -*-
import logging

from grab import Grab
from grab.error import GrabTimeoutError
from grab.spider import Spider, Task

from realtyboard.settings import PROXY_CREDENTIALS

logging.basicConfig(level=logging.DEBUG)


class SpiderCconfig(Spider):
    pass


class ProxyChecker(Spider):
    initial_urls = [
        u'http://ci.ua',
    ]
    proxy_list = []
    good_proxies = {}
    bad_proxies = []
    count = 0
    
    def prepare(self):
        print '//////////prepare///////////'
        try:
            f = open('realtyboard/media/proxy/fine_all_proxy.txt')
            self.proxy_list = [x.strip() for x in f.readlines()]
        finally:
            f.close()
    
    def create_grab_instance(self, **kwargs):
        print('///////create grab instance/////////// count = ', self.count)
        g = super(ProxyChecker, self).create_grab_instance(**kwargs)
        g.setup(proxy=self.proxy_list[self.count],
                proxy_userpwd=PROXY_CREDENTIALS['fine'],
                connect_timeout=6)
        self.count += 1
        return g
    
    def task_generator(self):
        print '//////////////task generator///////////////'
        for proxy in self.proxy_list:
            yield Task('check_proxy', url='http://ci.ua', delay=3,
                       network_try_limit=1, raw=True)
    
    def task_check_proxy(self, grab, task):
        if grab.response.error_code:
            self.bad_proxies.append(grab.config['proxy'])
            print ('////////bad///////// ', grab.config['proxy'],
                   grab.response.error_msg)
        else:
            self.good_proxies[grab.config['proxy']] = grab.response.body
            print ('//////good///////// ', grab.config['proxy'],
                   grab.response.code)
    
    def task_check_proxy_fallback(self, task):
        self.bad_proxies.append(grab.config['proxy'])
        print '////////fallback///////// ', grab.config['proxy']