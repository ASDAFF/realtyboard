import xlrd
import os

from django.core.management.base import BaseCommand, CommandError

from slparser.domria_metro import SUB_CIUA
from realtyboard.settings import PROJECT_PATH
from board.models import Advert
from time import time


path_xls = os.path.join(PROJECT_PATH, '123.xls')

xlsfile = xlrd.open_workbook(path_xls)
sheet= xlsfile.sheet_by_index(0)

def xls_importer(*args):  
    for r in range(1, sheet.nrows):
        advert = Advert()
        sub = sheet.cell(r,0).value
        advert.sublocality_id = SUB_CIUA[sub]
        advert.main_text = sheet.cell(r,1).value
        advert.price_uah = sheet.cell(r,2).value
        advert.raw_phones = sheet.cell(r,3).value
        advert.category_id = 11
        advert.city_id = 20
        advert.save()
        print r
print "Fin!!!!"


class Command(BaseCommand):

    def handle(self, *args, **options):
        o = xls_importer()
        t1 = time()
        print("Total time %s" % (time() - t1))
        self.stdout.write('Successfully import data')