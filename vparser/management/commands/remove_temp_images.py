from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from vparser.tasks import remove_images_4_days_ago_task

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                         make_option('--remove_images_4_days_ago_task',
                                     action='store_true',
                                     dest='remove_images_4_days_ago_task',
                                     default=False,
                                     help='remove_images_4_days_ago_task'),
                         )

    def handle(self, *args, **options):
        t1 = time()

        remove_images_4_days_ago_task()


        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')