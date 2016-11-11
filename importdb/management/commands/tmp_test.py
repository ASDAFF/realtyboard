import os
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import time
from importdb.import_cost import cost_next
from importdb.check_advert_for_middleman import check_advert_for_middleman

from board.models import *
from realtyboard.settings import PROJECT_PATH

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--cost',
                    action='store_true',
                    dest='cost',
                    default=False,
                    help='Import advert cost'),
    )

    def handle(self, *args, **options):
        t1 = time()

        # check_advert_for_middleman()
        self.send_cat_information()


        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')


    def send_cat_information(self):
        cat = Category.objects.all()
        cy = City.objects.get(id=20)
        file = open('/data/python/track.ci.ua/information_about_cat.txt', 'w')
        for c in cat:
            # print c.name
            # new_seo = Seo()
            # new_seo.name = c.name
            # new_seo.title = c.title
            # new_seo.seo_text = c.seo_text
            # new_seo.url = c.get_absolute_url()
            # new_seo.description = c.description
            # new_seo.type = None
            # new_seo.city_id = cy.id
            # new_seo.save()


            # name = c.name
            file.write("%s\n" % c.id)
            file.write("%s\n" % c.name.encode('utf-8'))
            file.write("%s\n" % c.title.encode('utf-8'))
            file.write("%s\n" % c.seo_text.encode('utf-8'))
            file.write("%s\n" % c.description.encode('utf-8'))
            file.write("%s\n" % c.get_absolute_url().encode('utf-8'))
            file.write(' '+"\n")

        file.close()

