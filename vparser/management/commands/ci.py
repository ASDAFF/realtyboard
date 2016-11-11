# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from vparser.ci import *
from vparser.utils import *
import urllib2

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--ci',
                    action='store_true',
                    dest='ci',
                    default=False,
                    help='Pareser ci just parser'),
    )

    def handle(self, *args, **options):
        t1 = time()

        ci()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')