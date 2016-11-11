# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
# from django.core.mail import send_mail

from slparser.pars_olx import OlxSpider


class Command(BaseCommand):

    def handle(self, *args, **options):
        o = OlxSpider(city=args[0],
                      network_try_limit=3,
                      thread_number=1,
                      depth=30)
        o.run()
        print o.stats
        # send_mail(u"parser stats %s" % args[0], str(o.stats), 'noreply@ci.ua', ['slavugan@gmail.com',], fail_silently=True)
