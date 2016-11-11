# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import utc
import os, shutil, sys

from board.models import *
from importdb.models import *
from importdb.utils import EXCLUDE_CAT
from realtyboard.settings import PROJECT_PATH

CHANGES_FOR_IMPORT_TERMINAL = {1: 4, 2: 1, 10: 1}


def port_terminal():
    one_month = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(days=30)  # two days ago
    # one_month = datetime.date.today() - datetime.timedelta(days=30)  # two days ago
    print one_month

    # for advert in Slandos.objects.filter(date__gte=two_one_ago):
    user_id = UserData.objects.get(id=8606)
    city_id = City.objects.get(id=20)

    for advert in Prorings.objects.all().exclude(site='ci.ua'):
        # advert = Prorings.objects.get(id=2441162)
        path_tmp = 'vparser/tmp/img/%s_%s.jpg' % (advert.id, '0')

        if os.path.isfile(path_tmp) or advert.status == 1:
            board = Advert()
            id_proring = advert.id
            piece = advert.text
            piece = piece[12:40].encode('utf-8')

            # adv = Advert.objects.filter(main_text__contains=piece, link=advert.link, date_of_update__gte=one_month).first()
            adv = Advert.objects.filter( author_id='8606', date_of_update__gte=one_month, main_text__contains=piece).first()
            try:
                print 'adv.id=', adv.id
                print 'adv.site=', adv.site
            except:
                pass
            if adv:
                # adv.date_of_update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                adv.date_of_update = datetime.datetime.utcnow().replace(tzinfo=utc)
                if not adv.price_uah:
                    if advert.cost:
                        adv.price_usd = parse_int(advert.cost)

                try:
                    if not adv.extraflat.rooms_number:
                        num_of_room(advert, adv)
                except Exception, ex:
                    print ex
                print 'UPDATE'
                adv.save()
            elif advert.cat != 100 and advert.status != 777:
                print u'write advert'
                if advert.title:
                    board.title = advert.title
                board.author = user_id
                board.category = exclude_cat(advert)
                board.city = city_id
                board.price_unit = '1'
                board.main_text = advert.text
                board.raw_phones = advert.phone1+','+advert.phone2+','+advert.phone3
                board.price_uah = parse_int(advert.cost)
                board.date_of_update = datetime.datetime.utcnow().replace(tzinfo=utc)
                board.creation_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                board.link = advert.link
                board.seller = int(CHANGES_FOR_IMPORT_TERMINAL[int(advert.status)])
                board.sublocality = board.detect_sublocality()
                board.site = advert.site
                print board.site
                board.vparser = advert.id

                board.save()

                if advert.room:
                    num_of_room(advert, board)
                print 'board for move photo=', board.id
                move_photo(board, id_proring)

    user_id.phone_set.clear()




def exclude_cat(advert):
    print advert.cat
    if advert.cat in EXCLUDE_CAT:
        cat_id = EXCLUDE_CAT[advert.cat]
        cat_id = Category.objects.get(id=cat_id)
    else:
        sl = Slandos.objects.get(id=advert.id)
        if sl.ci_cat:
            cat_id = Category.objects.get(id=sl.ci_cat)
        else:
            cat_id = Category.objects.get(id=advert.cat)
    return cat_id


def move_photo(board, id_proring):
    for i in xrange(0, 15):
        try:
            print 'board.id = ', board.id
            photo_id = Advert.objects.get(id=board.id)
            name = '%s_%s.jpg' % (id_proring, i)
            path_tmp = '%s/vparser/tmp/img/%s_%s.jpg' % (os.path.split(PROJECT_PATH)[0], id_proring, i)
            media_folder = os.path.join(settings.MEDIA_ROOT, name[:2])

            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            media = os.path.join(settings.MEDIA_ROOT, name[:2], name)

            if photo_id and os.path.isfile(path_tmp):
                shutil.copy(path_tmp, media)
                ph = "%s/%s" % (name[:2], name)
                Photo.objects.get_or_create(
                    advert=photo_id,
                    photo=ph)
        except Exception, ex:
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
            print ex

def test_photo():
    board = Advert.objects.get(id=405141)
    id_proring = 3981391
    for i in xrange(0, 15):
        try:
            print 'board.id = ', board.id
            photo_id = Advert.objects.get(id=board.id)
            name = '%s_%s.jpg' % (id_proring, i)
            path_tmp = '%s/vparser/tmp/img/%s_%s.jpg' % (os.path.split(PROJECT_PATH)[0], id_proring, i)
            media_folder = os.path.join(settings.MEDIA_ROOT, name[:2])

            if not os.path.exists(media_folder):
                os.makedirs(media_folder)

            media = os.path.join(settings.MEDIA_ROOT, name[:2], name)

            if photo_id and os.path.isfile(path_tmp):
                shutil.copy(path_tmp, media)
                ph = "%s/%s" % (name[:2], name)
                Photo.objects.get_or_create(
                    advert=photo_id,
                    photo=ph)
        except Exception, ex:
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
            print ex


def num_of_room(advert, board):
    if advert.room:
        board.extraflat = ExtraFlat(rooms_number=int(parse_int(advert.room)),)
    try:
        board.extraflat.save()
    except Exception, ex:
        print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
        print ex


