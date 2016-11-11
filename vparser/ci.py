# -*- coding: utf-8 -*-
from board.models import Advert, City
from importdb.models import Slandos
from personal.models import UserData
from django.utils.timezone import utc
import datetime
import sys


EXCLUDE_CAT_MOROZ = {11: 11, 12: 11, 14: 14, 16: 14, 17: 17, 21: 21, 22: 21, 24: 21,  27: 27, 26: 27}

two_days = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=2)
user_id = UserData.objects.get(id=8606)
city_id = City.objects.get(id=20)


def ci():
    for adv in Advert.objects.filter(date_of_update__gte=two_days, site=None, city=city_id):
        slando = Slandos()
        slando.title = adv.title
        slando.text = adv.main_text
        slando.cost = adv.price_uah if adv.price_uah else ''
        try:
            if adv.extraflat.rooms_number:
                slando.room = adv.extraflat.rooms_number
        except Exception, ex:
            print ex, 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)

        slando.status = 0
        slando.link = adv.id
        slando.cat = str(EXCLUDE_CAT_MOROZ[adv.category.id]) if adv.category.id in EXCLUDE_CAT_MOROZ else '100'
        slando.ci_cat = adv.category.id
        slando.date = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y-%m-%d")
        slando.site = 'ci.ua'

        ph = adv.phone_set.all()

        if len(ph):
            if len(ph) >= 1:
                slando.phone1 = '0'+str(ph[0].phone)
            if len(ph) >= 2:
                slando.phone2 = '0'+str(ph[1].phone)
            if len(ph) >= 3:
                slando.phone3 = '0'+str(ph[2].phone)

            slando.save()
        print adv.id, adv.date_of_update

