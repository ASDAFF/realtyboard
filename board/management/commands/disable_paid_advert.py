# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from board.models import Advert, PaidAdvert
import datetime
from django.utils import timezone
from django.utils.timezone import utc

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--disable advert',
                    action='store_true',
                    dest='disable advert',
                    default=False,
                    help='disable advert'),
    )

    def handle(self, *args, **options):
        pd = PaidAdvert.objects.filter(expiration_date__lte=timezone.now())
        for aa in pd:
            Advert.objects.get(id=aa.advert_id).disable_service(aa.service)
        
        pd_mail_three = PaidAdvert.objects.filter(
            expiration_date=timezone.now() + datetime.timedelta(days=3))
        pd_mail_one = PaidAdvert.objects.filter(
            expiration_date=timezone.now() + datetime.timedelta(days=1))
        if pd_mail_three:
            for m in pd_mail_three:
                m.advert.author.send_mail(10, day=u'Через 3 дня', advert=m.advert)
        if pd_mail_one:
            for m in pd_mail_one:
                m.advert.author.send_mail(10, day=u'Завтра', advert=m.advert)


