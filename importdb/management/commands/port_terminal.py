from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.utils import *
from importdb.smart_migrate_advert import port_terminal, test_photo
from board.models import *
from django.db.models.loading import get_model

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--port_terminal',
                                     action='store_true',
                                     dest='uufk',
                                     default=False,
                                     help='Import advert from mysqldb kohana'),
                         )

    def handle(self, *args, **options):
        t1 = time()

        if args:
            if args[0] == 'test_img':
                test_photo()
        else:
            port_terminal()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')