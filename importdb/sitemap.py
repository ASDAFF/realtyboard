# -*- coding: utf-8 -*-
import datetime, math, os
from django.utils import timezone
from django.utils.timezone import utc

from board.models import Category, Advert, City, Seo
from news.models import News
from realtyboard.settings import PROJECT_PATH

two_day = timezone.now() - datetime.timedelta(days=2)


def base_sitemap():
    file = open('%s/sitemap.xml' % os.path.split(PROJECT_PATH)[0], 'w')
    # file = open('/data/python/estate-kharkov.ci.ua/sitemap1.xml', 'w')
    # file = open('/data/python/estate-kharkov.ci.ua/realtyboard/static/sitemap.xml', 'w')
    file.write('<?xml version="1.0" encoding="UTF-8"?>'+"\n")
    file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n")

    file.write('<url>'+"\n")
    file.write('<loc>http://ci.ua/novosty</loc>'+"\n")
    file.write('<changefreq>weekly</changefreq>'+"\n")
    file.write('</url>'+"\n")

    file.write('<url>'+"\n")
    file.write('<loc>http://ci.ua/statiy/poleznoe</loc>'+"\n")
    file.write('<changefreq>weekly</changefreq>'+"\n")
    file.write('</url>'+"\n")

    cats = Category.objects.all().order_by('id')
    cites = City.objects.all()
    for city in cites:
        for cat in cats:
            file.write('<url>'+"\n")
            file.write(('<loc>http://ci.ua%s</loc>'+"\n") % cat.get_absolute_url_sitemap(city=city.slug))
            file.write('<changefreq>daily</changefreq>'+"\n")
            if city.slug == 'kharkov':
                file.write('<priority>1.0</priority>'+"\n")
            file.write('</url>'+"\n")

    # advs = Advert.objects.filter(date_of_update=datetime.date.today())
    # for adv in advs:
    #     file.write('<url>'+"\n")
    #     file.write(('<loc>http://ci.ua%s</loc>'+"\n") % adv.get_absolute_url())
    #     file.write('<changefreq>monthly</changefreq>'+"\n")
    #     if adv.city.slug == 'kharkov':
    #         file.write('<priority>1.0</priority>'+"\n")
    #     file.write('</url>'+"\n")

    news = News.objects.filter(category__slug='novosty').order_by('-creation_date')
    for new in news:
        file.write('<url>'+"\n")
        file.write(('<loc>http://ci.ua%s</loc>'+"\n") % new.get_absolute_url())
        file.write('<changefreq>monthly</changefreq>'+"\n")
        file.write('</url>'+"\n")

    news = News.objects.filter(category__slug='statiy/poleznoe').order_by('-creation_date')
    for new in news:
        file.write('<url>'+"\n")
        file.write(('<loc>http://ci.ua%s</loc>'+"\n") % new.get_absolute_url())
        file.write('<changefreq>monthly</changefreq>'+"\n")
        file.write('</url>'+"\n")



    file.write('</urlset>'+"\n")
    file.close()


def seo_sitemap():
    count = Seo.objects.all().count()/50000.
    count = int(math.ceil(count))

    if count > 1:
        for n in xrange(2, count):
            file = open('%s/sitemap%s.xml' % (os.path.split(PROJECT_PATH)[0], n), 'w') 
            file.write('<?xml version="1.0" encoding="UTF-8"?>'+"\n")
            file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n")

            after = 50000*(n-1)
            until = after - 50000

            for i in Seo.objects.all()[until:after]:
                if '/' in i.url:
                    file.write('<url>'+"\n")
                    pre = ('<loc>http://ci.ua%s</loc>'+"\n") % i.url.encode('utf-8')
                    file.write(pre.replace('&','&amp;'))
                    file.write('<changefreq>monthly</changefreq>'+"\n")
                    file.write('</url>'+"\n")

            file.write('</urlset>'+"\n")
            file.close()
    else:
        file = open('%s/sitemap2.xml' % os.path.split(PROJECT_PATH)[0], 'w')
        file.write('<?xml version="1.0" encoding="UTF-8"?>'+"\n")
        file.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n")

        for i in Seo.objects.all()[:50000]:
            if '/' in i.url:
                file.write('<url>'+"\n")
                pre = ('<loc>http://ci.ua%s</loc>'+"\n") % i.url.encode('utf-8')
                file.write(pre.replace('&','&amp;'))
                file.write('<changefreq>monthly</changefreq>'+"\n")
                file.write('</url>'+"\n")

        file.write('</urlset>'+"\n")
        file.close()

def advert_sitemap():
    pass
    # for city in City.objects.all():
    #
    # for adv in Advert.objects.filter(date_of_update__gte=two_day)[:49000]:
    #     file.write('<url>'+"\n")
    #     file.write(('<loc>http://ci.ua%s</loc>'+"\n") % adv.get_absolute_url())
    #     file.write('<changefreq>monthly</changefreq>'+"\n")
    #     # if adv.city.slug == 'kharkov':
    #     #     file.write('<priority>1.0</priority>'+"\n")
    #     file.write('</url>'+"\n")


def sitemap():
    # count = Seo.objects.all().count()/50000.
    # count = int(math.ceil(count))
    #
    #
    # file = open('/data/python/estate-kharkov.ci.ua/sitemap.xml', 'w')
    #
    # file.write('<?xml version="1.0" encoding="UTF-8"?>'+"\n")
    #
    # file.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"\n")
    #
    # file.write('<sitemap>'+"\n")
    # file.write('<loc>http://ci.ua/sitemap1.xml</loc>'+"\n")
    # file.write(('<lastmod>%s</lastmod>'+"\n") % timezone.now())
    # file.write('</sitemap>'+"\n")
    #
    #
    # if count >= 1:
    #     for n in xrange(2, count+2):
    #         file.write('<sitemap>'+"\n")
    #         file.write(('<loc>http://ci.ua/sitemap%s.xml</loc>'+"\n") % n)
    #         file.write(('<lastmod>%s</lastmod>'+"\n") % timezone.now())
    #         file.write('</sitemap>'+"\n")
    #
    #
    # file.write('</sitemapindex>'+"\n")
    #
    # file.close()



    base_sitemap()

    # seo_sitemap()