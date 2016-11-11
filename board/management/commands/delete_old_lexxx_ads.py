# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from board.models import Advert

class Command(BaseCommand):
    help = 'Delete old adverts where Lexxx is author.'
    
    def handle(self, *args, **options):
        old_date = datetime.date.today() - datetime.timedelta(days=180)
        ads = Advert.objects.filter(date_of_update__lt=old_date, 
                                    author_id=8606
                                   ).order_by('date_of_update')[:20] 
        for ad in ads:
            ad.delete()
        
        print('20 old adverts was deleted') 
        