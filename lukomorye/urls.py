# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from lukomorye.views import GallaryView, HomeView

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(template_name='lukomorye/main.html')),
    url(r'^/contacts$', TemplateView.as_view(template_name='lukomorye/contacts.html')),
    url(r'^/mestoraspolozhenie$', TemplateView.as_view(template_name='lukomorye/location.html')),
    url(r'^/opisanie$', TemplateView.as_view(template_name='lukomorye/opisanie.html')),
    url(r'^/plan$', TemplateView.as_view(template_name='lukomorye/plan.html')),
    url(r'^/gallary$', GallaryView.as_view(template_name='lukomorye/gallary.html')),
)