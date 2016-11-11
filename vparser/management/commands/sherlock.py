# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from vparser.parser_for_all_cities import *
from vparser.utils import *
from vparser.test_for_some_site import test_site
import urllib2

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--proxy_fine',
                    action='store_true',
                    # dest='proxy_fine',
                    default=False,
                    help='Update proxy "fineproxy"'),
        make_option('--proxy_box',
                    action='store_true',
                    # dest='proxy_box',
                    default=False,
                    help='Update proxy "proxy_box"'),
        make_option('--proxy_checker',
                    action='store_true',
                    # dest='proxy_box',
                    default=False,
                    help='Check proxy. It have argument [name of service]'),
        make_option('--test',
                    action='store_true',
                    # dest='ww',
                    default=False,
                    help='The custom test'),
        make_option('--city',
                    action='store_true',
                    # dest='ww',
                    default=False,
                    help='The option for running a some city, have two arguments [name of city] [count of thread] [proxy]'),
    )

    def handle(self, *args, **options):
        t1 = time()
        if options.get('proxy_fine'):
            get_proxy_fineproxy()
            self.stdout.write(u'fine_proxy have been updated.')
        if options.get('proxy_box'):
            get_proxy_box()
            self.stdout.write( u'proxy_box have been updated.')
        if options.get('test'):
            # test_premier()
            # test_slandos()
            test_site()
            self.stdout.write( u'some sith have been tested.')
        if options.get('proxy_checker'):
            site = ProxyCheker(thread_number=400, network_try_limit=1, service_proxy=args[0])
            site.run()
            self.stdout.write(u'proxies have been checked.')
        if options.get('city'):
            self.stdout.write( u'running multithreading')
            site = SiteStructureParser( city_pars=args[0], thread_number=int(args[1]), service_proxy=args[2])
            site.run()
            print 'count of thread = ', args[0]
            self.stdout.write(str(args[0])+u' have been worked.')

        print "Total time %s" % (time() - t1)
        self.stdout.write('Successfully import data')