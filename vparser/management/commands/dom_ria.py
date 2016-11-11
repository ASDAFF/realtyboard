from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from vparser.dom_ria import *
import urllib2

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--dom_ria',
                                     action='store_true',
                                     dest='slando',
                                     default=False,
                                     help='Pareser slando just parser'),
                         )

    def handle(self, *args, **options):
        t1 = time()
        #dom_ria()
        site = SiteStructureParser()
        site.run()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')