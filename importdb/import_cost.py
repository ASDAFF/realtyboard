# -*- coding: utf-8 -*-
from importdb.models import Kharkovs
from board.models import Advert
from board.utils import parse_int


def cost_next():
    for ci in Kharkovs.objects.all():
        try:
            print 'do', ci.id
            advert = Advert.objects.get(id=ci.id)
            if ci.currency and ci.currency == '1':
                advert.price_usd = parse_int(ci.cost)
                print '$', advert.price_usd
            elif ci.currency and ci.currency == '2':
                advert.price_uah = parse_int(ci.cost)
                print u'uah', advert.price_uah
            else:
                advert.price_uah = parse_int(ci.cost)
                print u'uah', advert.price_uah
        except Advert.DoesNotExist:
            print u'Нету'