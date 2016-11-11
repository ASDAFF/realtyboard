# -*- coding: utf-8 -*-
from ckeditor.fields import RichTextField
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponseRedirect
from django.utils import timezone

from board.models import City, Phone
from personal.models import UserData


# NEWS_CHOICES = (
#     (0, u'Без категории'),
#     (1, u'Новости недвижимости'),
#     (2, u'Нововведения сайта'),
#     (3, u'Задаваемые вопросы'),
#     (4, u'Полезные статьи')
# )

class NewsCategory(models.Model):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


class News(models.Model):
    category = models.ForeignKey(NewsCategory, verbose_name=u'Рубрика')
    title = models.CharField(max_length=255)
    # slug = models.CharField(max_length=400)
    slug = models.CharField(max_length=255, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    foreword = models.TextField(max_length=1000)
    article = RichTextField(verbose_name=u'Текст', max_length=4000)
    # article = models.TextField(verbose_name=u'Текст', max_length=4000)  #  blank=True, null=True
    key_words = models.TextField(max_length=1000)
    description = models.TextField(max_length=1000)
    author = models.ForeignKey(UserData, blank=True, null=True)
    # seller = models.SmallIntegerField(verbose_name=u'Категории', choices=NEWS_CHOICES, blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.title, self.foreword)

    def get_absolute_url(self):
        # return reverse('news-detail', kwargs={'slug': self.slug})
        return "/%s/%s" % (self.category.slug, self.slug)


class Comment(models.Model):
    news = models.ForeignKey(News)
    author_name = models.CharField(max_length=32)
    text = models.TextField(max_length=400)
    #pub_date = models.DateTimeField('date published', default='datetime.now')


class BlackList(models.Model):
    city = models.ForeignKey(City, verbose_name=u'Регион')
    author = models.ForeignKey(UserData)
    phone = models.ManyToManyField(Phone, verbose_name=u'Телефоны мошенников')
    address = models.CharField(max_length=80, verbose_name=u'Адрес мошенников', blank=True)
    text = models.TextField(verbose_name=u'Схема мошенничества')
    post_date = models.DateTimeField(
            default=timezone.now, verbose_name=u'Дата публикации')
    
    def get_absolute_url(sefl):
        return HttpResponseRedirect(reverse('black_list'))
    
    
class BlackListComment(models.Model):
    post = models.ForeignKey(BlackList)
    text = models.CharField(max_length=300)
    author = models.ForeignKey(UserData)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ["-id"]