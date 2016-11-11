# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from importdb.send_mail_to_moroz import *
from vparser.utils import *
import urllib2

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--mor',
                    action='store_true',
                    # dest='proxy_fine',
                    default=False,
                    help='Update proxy "fineproxy"'),
        make_option('--zov',
                    action='store_true',
                    # dest='proxy_box',
                    default=False,
                    help='Update proxy "proxy_box"'),
    )

    def handle(self, *args, **options):
        t1 = time()
        if options.get('mor'):
            send_mor()
        if options.get('proxy_box'):
            get_proxy_box()
            self.stdout.write( u'proxy_box have been updated.')

        print "Total time %s" % (time() - t1)
        self.stdout.write('Successfully import data')