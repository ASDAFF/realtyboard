# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand
from optparse import make_option

from realtyboard.settings import PROJECT_PATH
from board.models import Photo


class Command(BaseCommand):
    def handle(self, *args, **options):
        photos = Photo.objects.filter(advert__author_id=8606).only('photo', 'preview')
        for photo in photos:
            if not (os.path.isfile(photo.photo.path) and
                    os.path.isfile(photo.preview.path)):
                photo.delete()
        temp_dir = os.path.join(PROJECT_PATH)
        source_file = open(os.path.join(temp_dir ,'templates/del_foto.txt'), 'w')
        source_file.write('Del foto end')
        source_file.close()
