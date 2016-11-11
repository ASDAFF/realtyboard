# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from vparser.premier import *
from vparser.utils import *


#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--premier',
                    action='store_true',
                    dest='premier',
                    default=False,
                    help='Pareser premier just parser'),
    )

    def handle(self, *args, **options):
        t1 = time()

        get_proxy_hideme()

        if args:
            if args[0] == 'proxy':
                get_proxy_fineproxy()
                print u'update proxy'
            elif args[0] == 'test':
                pass
                # test_premier()
            elif args[0].isdigit():
                print u'running multithreading'
                site = SiteStructureParser(thread_number=int(args[0]))
                site.run()
        else:
            site = SiteStructureParser()
            site.run()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')