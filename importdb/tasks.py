# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from importdb.check_advert_for_middleman import to_day_phone_of_rieltor, check_advert_for_middleman
from importdb.sitemap import sitemap


@periodic_task(run_every=crontab(day_of_week='saturday', hour=4, minute=1))
def middleman():
    print("Running periodic task check_advert_for_middleman!")
    try:
        check_advert_for_middleman()
    except Exception, ex:
        print ex

    return 0


@periodic_task(run_every=crontab(hour=[9, 11], minute=1))
def middleman_today():
    print("Running periodic task check_advert_for_middleman!")
    try:
        to_day_phone_of_rieltor()
    except Exception, ex:
        print ex
    return 0


@periodic_task(run_every=crontab(hour=[4], minute=1))
def sitemap_today():
    print("Running periodic task sitemap!")
    try:
        sitemap()
    except Exception, ex:
        print ex
    return 0
