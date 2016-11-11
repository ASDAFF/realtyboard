# -*- coding: utf-8 -*-
import datetime, math
from django.core.management.base import BaseCommand
from django.utils import timezone

from board.models import Advert

class Command(BaseCommand):
    help = 'Delete old adverts where Lexxx is author.'
    
    def handle(self, *args, **options):
        today = timezone.now()
        delete_params = ({
                'categories': (31,32,34,36,37,41,42,44,46,47),
                'date': today - datetime.timedelta(days=30)
            }, {
                'categories': (21,22,24,26,27),
                'date': today - datetime.timedelta(days=90)
            }, {
                'categories': (11,12),
                'date': today - datetime.timedelta(days=180)
            }, {
                'categories': (14,16,17),
                'date': today - datetime.timedelta(days=360)
        })
        for item in delete_params:
            print 'for loop'
            del_ads(item['categories'], item['date'])


def del_ads(categories, date):
    id_list = Advert.objects.filter(
        author_id=8606, category_id__in=categories, date_of_update__lt=date
    ).order_by('date_of_update').values_list('id', flat=True)
    id_count = len(id_list)
    print('ids count: ', id_count)
    i_count = int(math.ceil(id_count/500.0))
    print('iter count: ', i_count)
    if i_count > 0:
        for x in xrange(i_count):
            print(x)
            x = x*500
            Advert.objects.filter(id__in=id_list[x:x+500]).delete()
