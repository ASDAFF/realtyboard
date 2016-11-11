import datetime

from django.core.management.base import BaseCommand, CommandError

from board.models import Advert, StatAdvert, City
from time import time


year = datetime.date.today().year
month = datetime.date.today().month
day = datetime.date.today().day - 1


DOMEN = { 
    "https://dom.ria":"Dom.ria",
    "http://domik.ua":"Domik.ua",
    "http://aviso.ua":"Aviso.ua",
    "http://fn.ua":"Fn.ua",
    "http://md.mirkvartir.ua":"Md.mirkvartir.ua",
    "http://mirkvartir.ua":"Mirkvartir.ua",
    "https://www.olx.ua":"Olx.ua",
    "http://premier.ua":"Premier.ua",
    "http://realt.ua":"Realt.ua",
}

REGION = {20,8}

def stats_parser(*args):

    last_day = Advert.objects.filter(date_of_update__range=["%s-%s-%s 00:00" %(year,month,day),
                                                            "%s-%s-%s 23:59" %(year,month,day)])


    for domen in DOMEN:
        addition = {'source' : domen}
        for city in REGION:
            adv_day = last_day.filter(link__startswith=domen, city_id= '%s' %(city))
            advert = StatAdvert()
            advert.city_id = city
            advert.source = DOMEN[addition['source']]
            advert.prodam_kvartiru = len(adv_day.filter(category_id=11))
            advert.prodam_komnatu = len(adv_day.filter(category_id=12))
            advert.prodam_dom = len(adv_day.filter(category_id=14))
            advert.prodam_uchastok = len(adv_day.filter(category_id=16))
            advert.prodam_nedvizhimost = len(adv_day.filter(category_id=17))
            advert.sdam_kvartiru = len(adv_day.filter(category_id=21))
            advert.sdam_komnatu = len(adv_day.filter(category_id=22))
            advert.sdam_dom = len(adv_day.filter(category_id=24))
            advert.sdam_uchastok = len(adv_day.filter(category_id=26))
            advert.sdam_nedvizhimost = len(adv_day.filter(category_id=27))
            advert.save()

class Command(BaseCommand):

    def handle(self, *args, **options):
        o = stats_parser()
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')