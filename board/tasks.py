# -*- coding: utf-8 -*-
"""
from __future__ import absolute_import

from celery.decorators import periodic_task
import datetime
from celery.task.schedules import crontab
from board.models import UserData, Advert
from personal.models import Group, UserMessage
from django.core.mail import send_mail, EmailMessage



@periodic_task(ignore_result=True, run_every=crontab(hour=13, minute=45))
def turn_off_user_of_base():
    # user = UserData.objects.filter(groups__name='abonent')
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
"""
# def update_mail():
#     advert = Advert.objects.filter(is_active=True, 
#                                    author_id__isnull=False, 
#                                    date_of_update=(datetime.date.today() - datetime.timedelta(days=7)))
#     rr = []
#     for a in advert:
#         if a.advert.author.id in rr:
#             pass
#         else:
#             rr.append(a.advert.author.id)
#             a.advert.author.send_mail(12)
#             set(rr)