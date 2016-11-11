# -*- coding: utf-8 -*-
from  importdb import models as importdb_models
from django.contrib import admin
from django.db.models.base import ModelBase
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response, redirect, render
from django.http import HttpResponse

# python magic don't try to understand!
for name, var in importdb_models.__dict__.items():
    if type(var) is ModelBase:
        try:
            admin.site.register(var)
        except:
            pass
