from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.utils import *
from importdb.utils import import_db_user
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

        import_db_user()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')