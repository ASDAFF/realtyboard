#!/usr/bin/env python
# -*- coding: utf-8 -*-
from hashlib import md5

import time
from random import randint
import functools
from time import sleep
import lxml
from lxml.html import fromstring
from cStringIO import StringIO

import urllib, urllib2, cookielib

def with_retry(func):
    '''
    Для реконекта к серверу
    '''
    @functools.wraps(func)
    def _retry(*args, **kwargs):        
        for x in xrange(0, 3):
            try:                
                return func(*args, **kwargs)
            except:                
                sleep(x*10)
        raise
    return _retry


class httpClient:
    def __init__(self, proxy=None, user_agent='Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.3) Gecko/20100423 Ubuntu/10.04 (lucid) Firefox/3.6.3'):      
        self.cookie_handler   = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.redirect_handler = urllib2.HTTPRedirectHandler()
        self.http_handler     = urllib2.HTTPHandler()
        self.https_handler    = urllib2.HTTPSHandler()

        self.opener = urllib2.build_opener(self.http_handler, self.https_handler, self.cookie_handler, self.redirect_handler)

        if proxy:
            self.proxy_handler = urllib2.ProxyHandler(proxy)
            self.opener.add_handler(self.proxy_handler)

        # Устанавливаем заголовок User-agent    
        self.opener.addheaders = [('User-agent', user_agent)]

        urllib2.install_opener(self.opener)

    @with_retry
    def request(self, url, params={}, timeout=30):
        try:
            if params:
                params = urllib.urlencode(params)
                html = urllib2.urlopen(url, params, timeout)
            else:            
                html = urllib2.urlopen(url, timeout=30)     
            return html.read()
        except:            
            return ""

    def add_header(self, headers):
        self.opener.addheaders = headers
        return False

    @with_retry     
    def get_file(self, url):
        try:
            u = urllib2.urlopen(url, timeout=30)
            return StringIO(u.read())
        except:
            return ""
            
    def save_file(self, url, name):
        u = urllib2.urlopen(url)        
        dfile = open(name, 'wb')        
        file_size_dl = 0
        block_sz = 8192 
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            dfile.write(buffer)
        dfile.close()
        
        return name