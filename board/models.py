# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.loading import get_model
from django.utils import timezone
from djangosphinx.models import SphinxSearch
from PIL import Image
from pytils.translit import slugify

import datetime, re
import logging
import os

from board.utils import parse_int, uah_to_usd, usd_to_uah
from personal.models import UserData, PaidService


# Get an instance of a logger
logger = logging.getLogger(__name__)

TERM_CHOICES = (
    (2, u'Длительно'),
    (1, u'Посуточно'),
)
SELLER_CHOICES = (
    (1, u'агентство'),
    (2, u'частный маклер'),
    (3, u'представитель хозяина, без комиссии'),
    (4, u'хозяин'),
    # (5, u'мошенник') он есть, но показывать его не нужно
)
PRICE_UNIT_CHOICES = (
    (1, u'за объект'),
    (2, u'за кв.м'),
    (3, u'за сотку')
)
CURRENCY_CHOICES = (
    (1, u'грн'),
    (2, u'$'),
)
AREA_UNIT = (
    (u'кв.метров', u'кв.метров'),
    (u'соток', u'соток'),
    (u'гектар', u'гектар'),
)
LOT_PURPOSE = (
    (u'земельный пай', u'земельный пай'),
    (u'ОСГ(особисте селянське господарство)', u'ОСГ(особисте селянське господарство)'),
    (u'под застройку', u'под застройку'),
    (u'садоводство', u'садоводство'),
    (u'рекреационного назначения', u'рекреационного назначения'),
    (u'коммерческого назначения', u'коммерческого назначения'),
)
GAZ_ELECTICITY = (
    (u'в доме', u'в доме'),
    (u'на участке', u'на участке'),
    (u'по улице', u'по улице'),
    (u'есть возможность подведения', u'есть возможность подведения'),
    (u'нет', u'нет'),
)
CONDITION_CHOICES = (
    (1, u'Без внутренних работ'),
    (2, u'Без ремонта'),
    (3, u'Ветхий дом'),
    (4, u'Евроремонт'),
    (5, u'Жилое'),
    (6, u'Капремонт'),
    (7, u'Косметический ремонт'),
    (8, u'Недострой'),
    (10, u'Строительный ремонт'),
    (12, u'Частичный ремонт'),
)

CHANGE_CITIES_NAME={
        u'Крым'         : u'Крыму',
        u'Винница'      : u'Виннице',
        u'Запорожье'    : u'Запорожье',
        u'Одесса'       : u'Одессе',
        u'Полтава'      : u'Полтаве',
        u'Ровно'        : u'Ровно',
        u'Сумы'         : u'Суммах',
        u'Тернополь'    : u'Тернополе',
        u'Хмельницкий'  : u'Хмельницке',
        u'Черкассы'     : u'Черкассах',
        u'Черновцы'     : u'Черновцах'
}

HOUSE_TYPE = ((1, u'Дом'), (2, u'Дача'))


def get_upload_path(instance, filename):
    return os.path.join(filename[:2], filename)


class Phone(models.Model):
    owner = models.ForeignKey(UserData, null=True, blank=True)
    advert = models.ManyToManyField('Advert', null=True, blank=True)
    phone = models.IntegerField(verbose_name=u'Телефон', unique=True)
    date_of_addition = models.DateField(verbose_name=u'Дата добавления', default=timezone.now)
    agent = models.SmallIntegerField(null=True, blank=True, choices=SELLER_CHOICES)
    main = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s" % (self.phone)
        
    def add_pro_comment(self, user, pro_comment):
        try:
            self.procomment_set.remove(self.procomment_set.get(user=user))
        except ObjectDoesNotExist:
            pass
        self.procomment_set.add(pro_comment)
        
    def add_pro_color_mark(self, user, color_mark):
        try:
            self.procolormark_set.remove(self.procolormark_set.get(user=user))
        except ObjectDoesNotExist:
            pass
        self.procolormark_set.add(color_mark)


class Seo(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True,  unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    seo_text = models.TextField(max_length=1000, blank=True, null=True)
    type = models.IntegerField(verbose_name=u'Тип', null=True)
    city = models.ForeignKey('City', verbose_name=u'Регион')
    key_words = models.TextField(max_length=1000, blank=True, null=True)


class PaidAdvert(models.Model):
    advert = models.ForeignKey('Advert')
    author = models.ForeignKey(UserData, blank=True, null=True)
    category = models.ForeignKey('Category', verbose_name=u'Рубрика', null=True, blank=True)
    expiration_date = models.DateField()
    city = models.ForeignKey('City', verbose_name=u'Регион', blank=True, null=True)
    service = models.ForeignKey(PaidService, verbose_name=u'Услуга')
    is_active = models.NullBooleanField(verbose_name=u'Активное', default=True)


class City(models.Model):
    name = models.CharField(max_length=25)
    slug = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    seo_text = models.TextField(max_length=1000, blank=True, null=True)
    name_pr = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']
        
    def get_absolute_url(self):
        return reverse('city', kwargs={'city': self.slug})

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Транслитерация имени категории для урла"""
        if self.slug is None or len(self.slug) == 0:
            self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)


class BigSublocality(models.Model):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Sublocality(models.Model):  
    city = models.ForeignKey(City)
    big_sublocality = models.ForeignKey(BigSublocality, blank=True, null=True)
    in_city = models.BooleanField(default=True)
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name


class Settlement(models.Model):
    name = models.CharField(max_length=30)
    sublocality = models.ForeignKey(Sublocality)


class MetroLine(models.Model):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

class Metro(models.Model):
    city = models.ForeignKey(City)
    line = models.ForeignKey(MetroLine, blank=True, null=True)
    name = models.CharField(max_length=40)
    sequence_number = models.IntegerField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['sequence_number']


class Street(models.Model):
    city = models.ForeignKey(City)
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ObjectType(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    parent = models.ForeignKey('Category', blank=True, null=True)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    seo_text = models.TextField(max_length=1000, blank=True, null=True)
    city = models.ForeignKey(City, verbose_name=u'Регион')
    action = models.BooleanField(verbose_name=u'Для всех категорий')
    list_region = models.TextField(max_length=4000, blank=True, null=True)
    key_words = models.TextField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self,):
        return reverse(
            'advert-category',
            kwargs={'category': self.slug, 'city': 'kharkov'})

    def get_absolute_url_sitemap(self, city):
        return reverse(
            'advert-category',
            kwargs={'category': self.slug, 'city': city})

    def seo_search(self):
        if self.action:
            for cat in Category.objects.all():
                for reg in self.list_region.split(','):
                    seo = Seo()
                    seo.name = cat.name+reg+self.city.name
                    seo.title = cat.name+reg+self.city.name
                    seo.description = cat.name+reg+self.city.name
                    seo.seo_text = cat.name+reg+self.city.name
                    sphinx = cat.name+' +'+reg+' +'+self.city.name
                    seo.url = cat.get_absolute_url_sitemap(self.city.slug)+u'?city=%s&text_filter=%s&sort_obj=date_of_update&sort_level=1' % (self.city.id,sphinx)
                    seo.type = 1
                    seo.save()
        else:
            for reg in self.list_region.split(','):
                seo = Seo()
                seo.name = self.name+reg+self.city.name
                seo.title = self.name+reg+self.city.name
                seo.description = self.name+reg+self.city.name
                seo.seo_text ='<h1>'+self.name+reg+self.city.name+'<h1>'
                sphinx = self.name+' +'+reg+' +'+self.city.name
                seo.url = self.get_absolute_url_sitemap(self.city.slug)+u'?city=%s&text_filter=%s&sort_obj=date_of_update&sort_level=1' % (self.city.id,sphinx)
                seo.type = 1
                seo.save()

    def save(self, *args, **kwargs):
        """Транслитерация имени категории для урла"""
        if self.list_region:
            self.seo_search()
        if self.slug is None or len(self.slug) == 0:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def has_parent(self):
        return True if self.parent else False

    def children(self):
        return self._meta.model.objects.filter(parent=self)


class MainCategory(models.Model):
    parent = models.ForeignKey('Category', blank=True, null=True)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    seo_text = models.TextField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self,):
        return reverse(
            'advert-category',
            kwargs={'category': self.slug, 'city': 'kharkov'})

    def save(self, *args, **kwargs):
        """Транслитерация имени категории для урла"""
        if self.slug is None or len(self.slug) == 0:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Photo(models.Model):
    photo = models.ImageField(upload_to=get_upload_path)
    advert = models.ForeignKey('Advert')
    alt = models.CharField(verbose_name=u'Комментарий к картинке', max_length=120, 
                           blank=True, null=True)
    order = models.IntegerField(verbose_name=u'Порядок', blank=True, null=True)
    preview = models.ImageField(upload_to=get_upload_path)

    class Meta:
        ordering = ['order']
        verbose_name = u'Фото'
        verbose_name_plural = u'Фото'

    def save(self, *args, **kwargs):
        size = (256, 256)
        # print "try to save"
        if not self.id and not self.photo:
            exit(0)
            return

        try:
            old_obj = Photo.objects.get(pk=self.pk)
            old_path = old_obj.photo.path
        except:
            pass

        thumb_update = False
        if self.preview:
            try:
                statinfo1 = os.stat(self.photo.path)
                statinfo2 = os.stat(self.preview.path)
                if statinfo1 > statinfo2:
                    thumb_update = True
            except:
                thumb_update = True

        pw = self.photo.width
        ph = self.photo.height
        nw = size[0]
        nh = size[1]

        if self.photo and not self.preview or thumb_update:
            filename = str(self.photo.path)
            image = Image.open(filename)
            # only do this if the image needs resizing
            if (pw, ph) != (nw, nh):
                pr = float(pw) / float(ph)
                nr = float(nw) / float(nh)

                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                if pr > nr:
                    # photo aspect is wider than destination ratio
                    tw = int(round(nh * pr))
                    image = image.resize((tw, nh), Image.ANTIALIAS)
                    l = int(round((tw - nw) / 2.0))
                    image = image.crop((l, 0, l + nw, nh))
                elif pr < nr:
                    # photo aspect is taller than destination ratio
                    th = int(round(nw / pr))
                    image = image.resize((nw, th), Image.ANTIALIAS)
                    t = int(round((th - nh) / 2.0))
                    image = image.crop((0, t, nw, t + nh))
                else:
                    # photo aspect matches the destination ratio
                    image = image.resize(size, Image.ANTIALIAS)

            image.save(self.get_preview_path())
            (a, b) = os.path.split(self.photo.name)
            self.preview = a + '/thumbs/' + b
            try:
                #os.remove(old_path)
                print(old_path)
                #os.remove(self.get_old_preview_path(old_path))
                print(self.get_old_preview_path(old_path))
            except:
                pass
        print "SUCCESS saved photo"
        return super(Photo, self).save()

    def get_preview_path(self):
        (head, tail) = os.path.split(self.photo.path)
        if not os.path.isdir(head + '/thumbs'):
            os.mkdir(head + '/thumbs')
        return head + '/thumbs/' + tail

    def get_old_preview_path(self, old_photo_path):
        (head, tail) = os.path.split(old_photo_path)
        return head + '/thumbs/' + tail

    def image_tag(self):
        return u'<img src="/media/%s" width="150px" />' % self.preview
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class Advert(models.Model):
    title = models.CharField(verbose_name=u'Заголовок', max_length=90, blank=True)
    slug = models.CharField(max_length=255, blank=True)
    author = models.ForeignKey(UserData, blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=u'Рубрика')
    price_uah = models.IntegerField(verbose_name=u'Цена Грн', null=True)
    price_usd = models.IntegerField(verbose_name=u'Цена $', null=True, blank=True)
    price_unit = models.SmallIntegerField(verbose_name=u'Цена указана за',
                                          choices=PRICE_UNIT_CHOICES,
                                          default=1, null=True,)  # type cost exsample - 'square meter'
    creation_date = models.DateTimeField(default=timezone.now)
    date_of_update = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    main_text = models.TextField(verbose_name=u'Текст объявления', max_length=1000)
    city = models.ForeignKey(City, verbose_name=u'Регион')
    metro = models.ForeignKey(Metro, verbose_name=u'Метро', blank=True, null=True)
    big_sublocality = models.ForeignKey(BigSublocality, blank=True, null=True)
    sublocality = models.ForeignKey(Sublocality, verbose_name=u'Район', blank=True, null=True)
    settlement = models.ForeignKey(Settlement, verbose_name=u'Населенный пункт', blank=True, null=True)
    contact_name = models.CharField(verbose_name=u'Контактное лицо', max_length=60, blank=True)
    raw_phones = models.CharField(verbose_name=u'Телефоны', max_length=100)
    seller = models.SmallIntegerField(verbose_name=u'Собственник / Посредник',
                                      choices=SELLER_CHOICES, blank=True, null=True)
    street = models.CharField(verbose_name=u'Улица', max_length=120, blank=True)
    is_active = models.NullBooleanField(verbose_name=u'Активное', default=True)
    link = models.CharField(verbose_name=u'Ссылка', max_length=2000, blank=True, null=True)
    site = models.CharField(verbose_name=u'Сайт', max_length=2000, blank=True, null=True)
    vparser = models.CharField(verbose_name=u'ID в slando', max_length=2000, blank=True, null=True)
    search = SphinxSearch()

    class Meta:
        ordering = ['-date_of_update']
        verbose_name = u'Объявление'
        verbose_name_plural = u'Объявления'

    def __unicode__(self):    
        return "%s - %s" % (self.title, self.creation_date)

    def get_absolute_url(self):
        if self.city_id:
            city_slug = self.city.slug
        else:
            city_slug = 'kharkov'
        return reverse('advert-detail', kwargs={'category': self.category.slug,
                                                'city': city_slug,
                                                'title': self.slug,
                                                'pk': self.pk})

    def get_phone_with_null_str(self):
        phones = []
        for phone in self.phone_set.all().values_list('phone', flat=True):
            if len(str(phone)) >= 8:
                phones.append('0'+str(phone))
            else:
                phones.append(str(phone))

        return ', '.join(phones)

    def get_photo_preview(self):
        photo = self.photo_set.first()
        return photo.preview if photo else 'nopic.gif'

    def save(self, *args, **kwargs):
        """Транслитерация имени для урла"""

        if self.title is None or len(self.title) == 0:
            sub = self.sublocality if self.sublocality else ""
            try:
                rooms = u", %s-комнатная" % self.extraflat.rooms_number
            except:
                rooms = u""
            self.title = u"%s %s%s" % (self.category.name if self.category else "", sub, rooms)
        if self.slug is None or len(self.slug) == 0:
            self.slug = slugify(self.title)

        if self.price_usd is None and self.price_uah:
            self.price_usd = uah_to_usd(self.price_uah)

        if self.price_uah is None and self.price_usd:
            self.price_uah = usd_to_uah(self.price_usd)


        # if self.author and not self.author.is_admin:
        if not self.author or not self.author.is_admin:
            for cut in  CuttingWords.objects.all():
                self.main_text = self.main_text.replace(cut.cut_words  ,'')

        super(Advert, self).save(*args, **kwargs)

        if self.raw_phones:
            current_phones = self.phone_set.all()
            current_numbers = current_phones.values_list('phone', flat=True)
            phones = [parse_int(x) for x in self.raw_phones.split(',')]
            for phone in phones:
                if phone not in current_numbers:
                    phone, c = Phone.objects.get_or_create(phone=phone)
                    self.phone_set.add(phone)
            for current_phone in current_phones:        
                if current_phone.phone not in phones:
                    self.phone_set.remove(current_phone)
                    
        super(Advert, self).save(*args, **kwargs)

    def price(self):
        if self.price_uah:
            return u"%s грн" % self.price_uah
        else:
            return ""

    def phones(self):
        return ", ".join(["0%s" % x if len(str(x.phone))>5 else "" for x in self.phone_set.all()])
        #return ", ".join(["0%s" % x for x in self.phone_set.all()])

    def get_raw_phones(self):
        return self.raw_phones.replace(" ","").split(',')

    def rooms_number(self):
        try:
            return self.extraflat.rooms_number
        except Exception, e:
            logger.error(e)
            return 0

    def get_related_managers(self):
        managers = []
        for related_object in self._meta.get_all_related_objects():
            try:
                managers.append(
                    getattr(self, related_object.get_accessor_name()))
            except:
                pass
        return managers

    def get_all_extrafield(self):
        fields = []
        for manager in self.get_related_managers():
            try:
                model = getattr(self, manager._meta.object_name.lower())
            except Exception, ex:
                ex
                continue
            for field in manager._meta.fields:
                try:
                    get_attr = getattr(model, field.name)
                    if get_attr and field.verbose_name != 'ID' and field.verbose_name != 'advert' and get_attr != '0':
                            fields.append((field.verbose_name, get_attr))
                except:
                    pass
        return fields

    def up_available(self):
        up_timedelta = timezone.now() - self.date_of_update
        if up_timedelta > datetime.timedelta(hours=12):
            return True
        else:
            return False

    def get_sublocality(self):
        return self.sublocality.name if self.sublocality else ""

    def get_metro(self):
        return self.metro.name if self.metro else ""

    def get_big_sublocality(self):
        return self.big_sublocality.name if self.big_sublocality else ""

    def get_contact_name(self):
        if self.contact_name:
            contacts = self.contact_name
        elif self.author:
            contacts = self.author.first_name
        else:
            contacts = False
        return contacts

    def detect_phone(self):
        phones = re.sub(r'[\s\-\(\)]', '', self.main_text)
        phones = re.findall(r'\d{10}(?=\D|$)', phones)
        if phones:
            return phones
        return None

    def detect_sublocality(self):
        markers = SublocalityDetect.objects.filter(city_id=self.city)
        title = re.sub(r'\s', '', self.title.lower())
        text = re.sub(r'\s', '', self.main_text.lower())
        for marker in markers:
            if marker.text in title or marker.text in text:
                return Sublocality.objects.get(id=marker.sublocality_id)
        return None

    def detect_metro(self):
        markers =MetroDetect.objects.filter(city_id=self.city)
        title = re.sub(r'\s', '', self.title.lower())
        text = re.sub(r'\s', '', self.main_text.lower())
        for marker in markers:
            if marker.text in title or marker.text in text:
                return Metro.objects.get(id=marker.metro_id)
        return None

    def detect_metro_id(self, marker_list):
        title = re.sub(r'\s', '', self.title.lower())
        text = re.sub(r'\s', '', self.main_text.lower())
        for marker in marker_list:
            if marker.text in title or marker.text in text:
                return marker.metro_id
        return None

    def detect_sublocality_id(self, marker_list):
        title = re.sub(r'\s', '', self.title.lower())
        text = re.sub(r'\s', '', self.main_text.lower())
        for marker in marker_list:
            if marker.text in title or marker.text in text:
                return marker.sublocality_id
        return None
        
    def activate_service(self, service, term, info=''):
        try:
            pp = PaidAdvert.objects.get(advert_id=self.id, service=service)
            pp.expiration_date += datetime.timedelta(days=term)
            info = info + u' продлено'
            pp.save()
        except:
            if timezone.now().hour > 15:
                term += 1
            pp = self.paidadvert_set.create(service=service,
                expiration_date=datetime.date.today()+datetime.timedelta(days=term))
        user = self.author
        print pp.expiration_date
        return user.useroperation_set.create(action=1,
                                      service=service, 
                                      info=info,
                                      term=term,
                                      expiration_date=pp.expiration_date,
                                      advert=self)
        
    def disable_service(self, service):
        pp = PaidAdvert.objects.filter(advert_id=self.id, service=service)
        pp.delete()
        user = self.author
        user.useroperation_set.create(action=2,
                                      service=service,
                                      info=u'объявление %s' % self.id,
                                      advert=self)

    def active_services(self):
        services = {}
        for paid in self.paidadvert_set.all():
            services[paid.service.name] = (paid.expiration_date - datetime.date.today()).days
        return services
        
    def add_pro_comment(self, user, pro_comment):
        try:
            self.procomment_set.remove(
                self.procomment_set.get(user=user))
        except ObjectDoesNotExist:
            pass
        self.procomment_set.add(pro_comment)
        
    def add_pro_color_mark(self, user, color_mark):
        try:
            self.procolormark_set.remove(self.procolormark_set.get(user=user))
        except ObjectDoesNotExist:
            pass
        self.procolormark_set.add(color_mark)
    
    def has_relatives(self):
        phones = self.phone_set.all()
        for phone in phones:
            if phone.advert.all().count() > 1:
                return True
        return False
            
    def count_relatives(self):
        phones = self.phone_set.all()
        ids = []
        for phone in phones:
            ids += list(phone.advert.all().values_list('id', flat=True))
        ids = len(list(set(ids)))
        if ids > 1:
            return ids-1
        else:
            return 0
    
    def ya_type(self):
        if self.category_id in [11,12,14,16]:
            return u"продажа"
        if self.category_id in [21,22,24,26]:
            return u"аренда"
            
    def ya_category(self):
        if 'kvartiru' in self.category.slug:
            return u'квартира'
        if 'komnatu' in self.category.slug:
            return u'комната'
        if 'dom' in self.category.slug:
            return u'дом'
        if 'uchastok' in self.category.slug:
            return u'участок'
            
    
class AdvertToDelete(models.Model):
    advert = models.OneToOneField(Advert)
    date_of_del = models.DateField(default=datetime.date.today())


class ExtraFlat(models.Model):
    advert = models.OneToOneField(Advert)
    rooms_number = models.SmallIntegerField(verbose_name=u'Кол-во комнат',
                                            max_length=2, blank=True, null=True)
    new_building = models.NullBooleanField(verbose_name=u'Новострой', blank=True, null=True)
    total_area = models.IntegerField(verbose_name=u'Общая площадь', blank=True, null=True)
    floor = models.SmallIntegerField(verbose_name=u'Этаж', blank=True, null=True)
    floors = models.SmallIntegerField(verbose_name=u'Этажность', blank=True, null=True)
    condition = models.IntegerField(verbose_name=u'Состояние', blank=True,
                                 choices=CONDITION_CHOICES, null=True)


class ExtraHouse(models.Model):
    advert = models.OneToOneField(Advert)
    total_area = models.IntegerField(verbose_name=u'Площадь дома, кв.м',
                                     blank=True, null=True)
    lot_area = models.IntegerField(verbose_name=u'Площадь участка', blank=True, null=True)
    lot_unit = models.CharField(verbose_name=u'Единица измерения', max_length=15,
                                blank=True, choices=AREA_UNIT)
    floors = models.SmallIntegerField(verbose_name=u'Этажность дома', blank=True, null=True)
    condition = models.IntegerField(verbose_name=u'Состояние', blank=True, null=True,
                                    choices=CONDITION_CHOICES)
    gaz = models.CharField(verbose_name=u'Газ', max_length=70, blank=True,
                           choices=GAZ_ELECTICITY)
    water = models.CharField(verbose_name=u'Вода', max_length=70, blank=True)
    electricity = models.CharField(verbose_name=u'Электричество', max_length=70,
                                   blank=True, choices=GAZ_ELECTICITY)
    house_type = models.SmallIntegerField(verbose_name=u'Тип', choices=HOUSE_TYPE,
                                          blank=True, null=True)

class ExtraLot(models.Model):
    advert = models.OneToOneField(Advert)
    lot_area = models.IntegerField(verbose_name=u'Площадь участка', blank=True, null=True)
    lot_unit = models.CharField(verbose_name=u'Единица измерения', max_length=32,
                                blank=True, choices=AREA_UNIT)
    intended_purpose = models.CharField(verbose_name=u'Назначение', max_length=40,
                                        blank=True, choices=LOT_PURPOSE)
    gaz = models.CharField(verbose_name=u'Газ', max_length=70, blank=True,
                           choices=GAZ_ELECTICITY)
    water = models.CharField(verbose_name=u'Вода', max_length=70, blank=True)
    electricity = models.CharField(verbose_name=u'Электричество', max_length=70,
                                   blank=True, choices=GAZ_ELECTICITY)


class ExtraRent(models.Model):
    advert = models.OneToOneField(Advert)
    term = models.SmallIntegerField(verbose_name=u'Период аренды', blank=True, null=True,
                                    choices=TERM_CHOICES)


class ExtraCommercial(models.Model):
    advert = models.OneToOneField(Advert)
    object_type = models.ForeignKey(ObjectType, verbose_name=u'Тип объекта', blank=True, null=True)


class SublocalityDetect(models.Model):
    text = models.CharField(max_length=30)
    city = models.ForeignKey(City)
    sublocality = models.ForeignKey(Sublocality)

    class Meta:
        verbose_name = u'Определение района'
        verbose_name_plural = u'Определение района'

    def __unicode__(self):
        return self.text


        
class MetroDetect(models.Model):
    text = models.CharField(max_length=30)
    city = models.ForeignKey(City)
    metro = models.ForeignKey(Metro)

    def __unicode__(self):
        return self.text

class Poll(models.Model):
    question = models.CharField(verbose_name=u'Вопрос на голосование', max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200, null=True)
    # votes = new_building = models.BooleanField()
    user = models.ForeignKey(UserData, blank=True, null=True)
    ip = models.CharField(max_length=255)
    phone = models.ForeignKey(Phone)
    advert = models.ForeignKey(Advert, null=True)
    pub_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.choice_text

class SeoGenerator(models.Model):
    city = models.ForeignKey('City', verbose_name=u'Регион', blank=True, null=True)
    first = models.TextField(max_length=4000)
    second = models.TextField(max_length=4000)
    third = models.TextField(max_length=4000)


    def seo_generator(self):
        for first in self.first.split(','):
            for second in self.second.split(','):
                for third in self.third.split(','):
                    tem = first+' '+second+' '+third+' '+self.city.name
                    seo = Seo()
                    seo.name = tem
                    seo.title = tem
                    seo.description = tem
                    seo.seo_text = tem
                    sphinx = first+'+'+second+'+'+third+'+'+self.city.name
                    seo.url = u'/board/search?just_text='+sphinx
                    seo.city = self.city
                    seo.type = 1
                    seo.save()


    def save(self, *args, **kwargs):
        self.seo_generator()

        super(SeoGenerator, self).save(*args, **kwargs)


class CuttingWords (models.Model):
    cut_words = models.CharField(verbose_name=u'Вырезаемый текст', max_length=200)
    all = models.BooleanField(verbose_name=u'Пройти по всем объявлениям (длительная операция)')


    def __unicode__(self):  # Python 3: def __str__(self):
        return self.cut_words


    def check_all(self):
        if self.all:
            for adv in Advert.objects.all():
                if not adv.author or not adv.author.is_admin:
                    adv.main_text = adv.main_text.replace(self.cut_words,'')
                    adv.save()


    def save(self, *args, **kwargs):
        self.check_all()
        super(CuttingWords, self).save(*args, **kwargs)


BANNER_PLACES = ((11, 'adv_detail_bottom_1'),
                 (12, 'adv_detail_bottom_2'),
                 (13, 'adv_detail_bottom_3'),)


class PaidBanner(models.Model):
    def get_banner_path(instance, filename):
        return os.path.join('banners', filename)

    img = models.ImageField(upload_to=get_banner_path)
    img_title = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateField()
    place = models.IntegerField(choices=BANNER_PLACES)
    city = models.ForeignKey(City)
    link = models.CharField(max_length=200)


class ProColorMark(models.Model):
    color = models.CharField(max_length=10)
    phone = models.ManyToManyField(Phone)
    advert = models.ManyToManyField(Advert)
    user = models.ForeignKey(UserData)

    class Meta:
        unique_together = ('color', 'user')
        

class ProComment(models.Model):
    text = models.CharField(max_length=100)
    phone = models.ManyToManyField(Phone)
    advert = models.ManyToManyField(Advert)
    user = models.ForeignKey(UserData)

    class Meta:
        unique_together = ('text', 'user')


class Complaint(models.Model):
    advert = models.ForeignKey(Advert, null=True, on_delete=models.SET_NULL)
    phones = models.ManyToManyField(Phone)
    user = models.ForeignKey(UserData, null=True, on_delete=models.SET_NULL)
    email = models.EmailField()
    reason = models.CharField(max_length=500)
    pub_date = models.DateTimeField(default=timezone.now)
    checked = models.BooleanField(default=False)


class MessageForUsers(models.Model):
    text = models.CharField(max_length=250)
    location = models.IntegerField(choices=((1, u'По всему сайту'),), primary_key=True)


class SpamWord(models.Model):
    word = models.CharField(max_length=100)


class StatAdvert(models.Model):
    city = models.ForeignKey(City, verbose_name=u'Регион')
    creation_date = models.DateField(default="%s-%s-%s" %(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day - 1))
    source = models.CharField(max_length=255, blank=True, null=True)
    prodam_kvartiru = models.CharField(max_length=255, verbose_name=u'Продам квартиру', blank=True, null=True)
    prodam_komnatu = models.CharField(max_length=255, verbose_name=u'Продам комнату', blank=True, null=True)
    prodam_dom = models.CharField(max_length=255, verbose_name=u'Продам дом', blank=True, null=True)
    prodam_uchastok = models.CharField(max_length=255, verbose_name=u'Продам участок', blank=True, null=True)
    prodam_nedvizhimost = models.CharField(max_length=255, verbose_name=u'Продам коммерческую недвижимость', blank=True, null=True)
    sdam_kvartiru = models.CharField(max_length=255, verbose_name=u'Сдам квартиру', blank=True, null=True)
    sdam_komnatu = models.CharField(max_length=255, verbose_name=u'Сдам комнату', blank=True, null=True)
    sdam_dom = models.CharField(max_length=255, verbose_name=u'Сдам дом', blank=True, null=True)
    sdam_uchastok = models.CharField(max_length=255, verbose_name=u'Сдам участок', blank=True, null=True)
    sdam_nedvizhimost = models.CharField(max_length=255, verbose_name=u'Сдам коммерческую недвижимость', blank=True, null=True)


