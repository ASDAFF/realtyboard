from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.utils import *
from board.models import *
from django.db.models.loading import get_model
#example: importdbm 30 kharkovs
#example: importdbm all kievs
#example: importdbm 1000 others
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--uufk',
                                     action='store_true',
                                     dest='uufk',
                                     default=False,
                                     help='Import advert from mysqldb kohana'),
                         )

    def handle(self, *args, **options):
        t1 = time()

        add_user_from_kohana(args[0])

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')
