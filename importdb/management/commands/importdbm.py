from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.utils import import_db
from board.models import *
from django.db.models.loading import get_model
#example: importdbm 30 kharkovs
#example: importdbm all kievs
#example: importdbm 1000 others


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--importdb',
                    action='store_true',
                    dest='importdb',
                    default=False,
                    help='Import advert from mysqldb kohana'),
    )

    def handle(self, *args, **options):
        t1 = time()

        if args:
            if args[0] == u'all' and len(args[1]):
                model = get_model('importdb', args[1])
                count = import_db(1000000, model)
            else:
                model = get_model('importdb', args[1])
                count = import_db(args[0], model)
        else:
            count = import_db(30)  # if hasn't chosen

            print("Total time %s, count %s" % (time() - t1, count))
            self.stdout.write('Successfully import data')
