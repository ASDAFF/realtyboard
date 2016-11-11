 # -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from vparser.gorod import *
from vparser.gorod import gorod
import urllib2

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--gorod',
                    action='store_true',
                    # dest='proxy_fine',
                    default=False,
                    help='Make and save file for Agency "Gorod"'),
    )

    def handle(self, *args, **options):
        t1 = time()

        if options.get('gorod'):
            gorod()
            self.stdout.write(u'the file have been done.')

        self.stdout.write("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')