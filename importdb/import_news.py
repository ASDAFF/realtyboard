# -*- coding: utf-8 -*-
from importdb.models import Stats
from news.models import News, NewsCategory
from personal.models import UserData
import string


def import_news():
    author = UserData.objects.get(id=1)
    print author.username
    for new_old in Stats.objects.all():
        if new_old.catid != 0 and (new_old.catid == 2 or new_old.catid == 3):
            print new_old.id, new_old.name, new_old.catid
            stci = News()

            print author
            # stci.id = new_old.id
            stci.article = new_old.full.replace('http://centrinform.info/', 'http://ci.ua/')
            stci.author = author
            stci.foreword = new_old.min.replace('http://centrinform.info/', 'http://ci.ua/')
            stci.slug = new_old.url
            stci.title = new_old.name
            stci.creation_date = new_old.dat_created
            stci.description = new_old.opisanie
            stci.key_words = new_old.klucheviki
            stci.category = NewsCategory.objects.get(id=new_old.catid)

            stci.save()
            # News.objects.get_or_create(
            #
            #     id=new_old.id,
            #     article=new_old.full.replace('http://centrinform.info/', 'http://ci.ua/'),
            #     author=author,
            #     foreword=new_old.min.replace('http://centrinform.info/', 'http://ci.ua/'),
            #     slug=new_old.url,
            #     title=new_old.name,
            #     creation_date=new_old.dat_created,
            #     description=new_old.opisanie,
            #     key_words=new_old.klucheviki,
            #     category=NewsCategory.objects.get(id=new_old.catid)
            # #   defaults={'category': NewsCategory.objects.get(id=new_old.catid)}  # default применится в случае create
            # )
            # new.article = new_old
            # # new.article = new_old.full.replace('http://centrinform.info/', 'http://ci.ua/')
            # new.author = author
            # new.category = NewsCategory.objects.get(id=new_old.catid)
            # new.foreword = new_old.min.replace('http://centrinform.info/', 'http://ci.ua/')
            # new.part_url = new_old.url
            # new.title = new_old.name
            # new.save()







        # try:
        #
        # except Stats.DoesNotExist:
        #     print u'Нету'