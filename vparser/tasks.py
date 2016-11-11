# -*- coding: utf-8 -*-
import datetime, os
from __future__ import absolute_import
from vparser import slando
from vparser import dom_ria
from vparser import est
from vparser import premier
from vparser import utils
from celery.decorators import periodic_task
# from datetime import timedelta
from celery.task.schedules import crontab

from realtyboard.settings import PROJECT_PATH


@periodic_task(run_every=crontab(hour=[6, 15], minute=30))
def slando_task():
    try:
        utils.get_proxy_fineproxy()
        # site = slando.SiteStructureParser(thread_number=25)
        # site.run()
    except Exception, ex:
        print ex
    print("Running periodic task SLANDO!")
    return {"task succes end"}


# @periodic_task(run_every=crontab(hour=[10, 15], minute=30))
# def premier_task():
#     try:
#         site = premier.SiteStructureParser(thread_number=25)
#         site.run()
#     except Exception, ex:
#         print ex
#     print("Running periodic task SLANDO!")
#     return {"task succes end"}


# @periodic_task(run_every=crontab(hour=[7, 16], minute=30))
# def dom_ria_task():
#     try:
#         site = dom_ria.SiteStructureParser(thread_number=25)
#         site.run()
#     except Exception, ex:
#         print ex
#     print("Running periodic task DOM_RIA!")


# @periodic_task(run_every=crontab(hour=[5, 14], minute=30))
# def est_task():
#     try:
#         site = est.SiteStructureParser(thread_number=25)
#         site.run()
#     except Exception, ex:
#         print ex
#     print("Running periodic task EST!")


@periodic_task(run_every=crontab(hour=[5, 14], minute=30))
def remove_images_4_days_ago_task():
    try:
        os.chdir('%s/vparser/tmp/img/' % os.path.split(PROJECT_PATH)[0])
        dirlist = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
        one_month = datetime.datetime.now() - datetime.timedelta(days=4)
        for i in dirlist:
            t = os.path.getmtime(i)
            if one_month > datetime.datetime.fromtimestamp(t):
                path_2 = os.path.join(PROJECT_PATH, '/vparser/tmp/img/', i)
                print datetime.datetime.fromtimestamp(t)
                os.remove(path_2)
    except Exception, ex:
        print ex
