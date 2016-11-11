# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.timezone import utc
from optparse import make_option
from time import time

from board.morozov import moroz

#example: manage.py port_terminal
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--morozov',
                    action='store_true',
                    dest='morozov',
                    default=False,
                    help='morozov'),
    )

    def handle(self, *args, **options):
        t1 = time()
        if options.get('morozov'):
            moroz()

        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')