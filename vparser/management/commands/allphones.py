from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
# from board.models import *
# from django.db.models.loading import get_model
from vparser.dom_ria import *
import urllib2
from vparser.allphones import get_allphones

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--allphones',
                                     action='store_true',
                                     dest='allphones',
                                     default=False,
                                     help='Pareser slando just parser'),
                         )

    def handle(self, *args, **options):
        t1 = time()

        get_allphones()


        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')