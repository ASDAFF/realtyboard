from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.check_advert_for_middleman import check_advert_for_middleman, to_day_phone_of_rieltor
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--check_phone',
                                     action='store_true',
                                     dest='check_phone',
                                     default=False,
                                     help='check_phone'),
                         )

    def handle(self, *args, **options):
        t1 = time()
        if args:
            if args[0] == 'all':
                check_advert_for_middleman()
            if args[0] == 'last':
                to_day_phone_of_rieltor()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')