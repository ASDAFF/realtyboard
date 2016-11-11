# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve
from board.utils import ab_required
from board.views import index, AdvertList
# from personal.admin_views import UserDataDetail

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT}),
    # url(r'^docs/kharkov/(?P<path>.*)$', ab_required(serve), {'document_root': settings.BAZADIR_KH}),
    url(r'^docs/(?P<path>.*)$', ab_required(serve), {'document_root': settings.BAZADIR}),#ab_required(serve),
    url(r'^accounts/', include('personal.urls')),
    url(r'^importdb/', include('importdb.urls')),
    url(r'^lukomorye-test', include('lukomorye.urls')),
    url(r'^tour/', include('tour.urls')),
    url(r'^lesnoe-test', include('lesnoe.urls')),
    url(r'^google2bd45c33013117d0\.html$', TemplateView.as_view(
        template_name='google2bd45c33013117d0.html')),
    url(r'^report.xml', TemplateView.as_view(
        template_name='report.xml')),
    url(r'^robots.txt', TemplateView.as_view(
        template_name='robots.txt')),
    url(r'^sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml')),
    url(r'^sitemap1.xml', TemplateView.as_view(
        template_name='sitemap1.xml')),
    url(r'^sitemap2.xml', TemplateView.as_view(
        template_name='sitemap2.xml')),
    url(r'^googleaecc78a1c9920200\.html$', TemplateView.as_view(
        template_name='googleaecc78a1c9920200.html')),
    url(r'^d96c75d0ae58\.html$', TemplateView.as_view(
        template_name='d96c75d0ae58.html')), # подтверждалка для uLogin
    url(r'^$', AdvertList.as_view(template_name='index.html'), name='board-main'),
    url(r'^', include('news.urls')),
    # url(r'^upload/(?P<file_name>.+)$', 'board.views.upload_file', 
    #     name='upload_file'),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^', include('board.urls')),
)
