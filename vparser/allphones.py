# -*- coding: utf-8 -*-
from importdb.models import Posredniks

def get_allphones():
    allphones = open('realtyboard/static/allphones.txt', 'w')
    for phone in Posredniks.objects.all():
        dd = str(phone.tel)
        ww = phone.opisanie.encode('utf-8')
        allphones.write(dd+"               "+ww+'\n')
    allphones.close()
    print 'len=', Posredniks.objects.count()





# proxy_list = pro_m['host']+':'+pro_m['port']
#         file_proxy.write(proxy_list+"\n")
#         proxy.append(proxy_list)