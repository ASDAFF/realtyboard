#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from pytesser import *
from PIL import ImageOps, ImageEnhance
from httpClient import *
import re


def myEqualize(im):
    im=im.convert('L')
    contr = ImageEnhance.Contrast(im)
    im = contr.enhance(0.3)
    bright = ImageEnhance.Brightness(im)
    #im = bright.enhance(2)
    #im.show()
    return im

def parse_image(url, proxy):    
    if proxy:        
        hc = httpClient(proxy=proxy)
    else:
        hc = httpClient()
    html = hc.request(url)
    if len(html)==0:
        return None
    img_url = "http://kharkov.kha.slando.ua/ajax/misc/contact/phone/%s/" % (re.findall(r'-ID(.*?).html', url)[0])   
    img = hc.request(img_url).replace("\\", "")
    if len(img)==0:
        return None
    real_image_url = re.findall(r'<img[^>]*\ssrc="(.*?)"', img)[0]
    img_file = hc.get_file(real_image_url)
    return Image.open(img_file)
    
if __name__ == "__main__":    
    if len(sys.argv)>1:
        filename = sys.argv[1]
        if len(sys.argv)>2:            
            #proxy_str = sys.argv[2].split(":")
            proxy = {'http': sys.argv[2]}#{"host":proxy_str[0], "port":proxy_str[1]}
        else:
            proxy = None
        image = parse_image(filename, proxy)
        if image is None:
            print(u"Номер не найден")
            exit(13)
        if '-e' in sys.argv:
            image = ImageOps.equalize(image)
        if '-m' in sys.argv:
            image = myEqualize(image)
        if '-b' in sys.argv:
            image = image.convert('1')
        print(image_to_string(image).strip())
    else:
        print("Enter valid image filename")
        exit(0)