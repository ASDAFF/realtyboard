# -*- coding: utf-8 -*-
import datetime

from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time

from personal.models import UserData

def turn_off_user_of_base():
    user = UserData.objects.filter(services__name__startswith='base_')
    for u in user:
        act_serv = u.services.all()
        for act in act_serv:
            expiration_date = u.get_exp_date(act.id)
            if not (expiration_date and not datetime.date.today() >= expiration_date):
                u.remove_ab_status(service=act, info=u'плановое отключение')
                u.send_mail(4)
                print 'User accesses have been disabled of base'
            elif expiration_date == datetime.date.today() + datetime.timedelta(days=3):
                u.send_mail(11, day=u'Через 3 дня')
                print 'User have been informed about disabled of base'
            elif expiration_date == datetime.date.today() + datetime.timedelta(days=1):
                u.send_mail(11, day=u'Завтра')
                print 'User have been informed about disabled of base'


#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--turn_off_user_of_base',
                    action='store_true',
                    dest='turn_off_user_of_base',
                    default=False,
                    help='turn_off_user_of_base'),
    )

    def handle(self, *args, **options):
        t1 = time()

        turn_off_user_of_base()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')

    