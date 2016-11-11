from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.import_news import import_news
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--import_news',
                                     action='store_true',
                                     dest='uufk',
                                     default=False,
                                     help='Import import_news'),
                         )

    def handle(self, *args, **options):
        t1 = time()

        import_news()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')