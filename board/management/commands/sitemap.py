# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.sitemap import sitemap

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--sitemap',
                    action='store_true',
                    dest='sitemap',
                    default=False,
                    help='sitemap'),
    )

    def handle(self, *args, **options):
        t1 = time()
        if options.get('sitemap'):
            sitemap()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')