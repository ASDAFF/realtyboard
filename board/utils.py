# -*- coding: utf-8 -*-
import functools, os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, request
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

from realtyboard.settings import USD_UAH


def parse_int(string):
    try:
        string = string.encode('utf-8')
        value = ''.join([x for x in str(string) if x.isdigit()])[-9:]
    except:
        return 0
    return int(value if len(value) else 0)

def parse_int_str(string):
    string = string.encode('utf-8')
    value = ''.join([x for x in str(string) if x.isdigit()])[-9:]
    return str(value if len(value) else 0)


def get_related_managers(model):
    managers = []
    for related_object in model._meta.get_all_related_objects():
        try:
            managers.append(getattr(model, related_object.get_accessor_name()))
        except:
            pass
    return managers


def uah_to_usd(c):
    return c/USD_UAH


def usd_to_uah(c):
    return c*USD_UAH


def sort_phone(phone_sttr, user):
    from board.models import Phone
    phones = phone_sttr.split(',')
    for phone in phones:
        phone_number = parse_int(phone)
        print 'raw_ph=', phone_number
        #import pdb;pdb.set_trace()
        phones, c = Phone.objects.get_or_create(phone=phone_number, defaults={'owner': user})
        # phones.owner = user
        phones.save()


def ab_required(func):
    @functools.wraps(func)
    def _ab_required(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        if request.user.is_admin:
            return func(request, *args, **kwargs)
        elif 'city' in kwargs:
            from board.models import City
            city = City.objects.get(slug=kwargs.get('city'))
            if request.user.is_abonent(city_id=city.id):
                return func(request, *args, **kwargs)
            else:
                return render(request, 'no_access.html', {'message': 
                        u'У вас нет доступа к базе без посредников по городу '\
                        + city.name + u'! Для получения доступа\
                        необходимо произвести оплату.'})
        elif request.user.services.all():
            return func(request, *args, **kwargs)
        else:
            return render(request, 'no_access.html', {'message': u'У вас нет доступа\
                          к базе без посредников! Для получения доступа нужно\
                          произвести оплату.'})
    return _ab_required


def ed_required(func):
    @functools.wraps(func)
    def _ab_required(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('login'))
    return _ab_required


def ed_required_redactor(func):
    @functools.wraps(func)
    def _ab_required(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))
        if request.user.is_staff or request.user.is_redactor():
            return func(request, *args, **kwargs)
        else:
             return HttpResponseRedirect(reverse('login'))
    return _ab_required


def with_reconnect(func):
    '''
    Для реконекта к фтп серверу
    '''
    @functools.wraps(func)
    def _reconnector(*args, **kwargs):
        for x in xrange(0, 20):
            try:
                return func(*args, **kwargs)
            except:
                sleep(10)
        raise
    return _reconnector


def rename_base_files(path_to_files):
    """renames files from 'd.m.Yxxx' to Y.m.dxxx"""
    os.chdir(path_to_files)
    file_names_list = os.listdir(path_to_files)
    for name in file_names_list:
        new_name = name[6:10]+'.'+name[3:5]+'.'+name[:2]+name[10:]
        os.rename(name, new_name)