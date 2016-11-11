# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from board.models import Advert, PaidAdvert
from django.utils import timezone
from django.utils.timezone import utc


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--auto_up',
                    action='store_true',
                    dest='auto_up',
                    default=False,
                    help='auto_up'),
    )

    def handle(self, *args, **options):
        t1 = time()
        pd = PaidAdvert.objects.filter(service=4)
        for aa in pd:
            aa.advert.date_of_update = timezone.now()
            print 'up_advert'
            aa.advert.save()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')