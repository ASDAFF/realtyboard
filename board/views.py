# -*- coding: utf-8 -*-
import datetime
from hashlib import md5
import json
import os
import re
import base64
from math import ceil
from time import time
import glob, random
import qrcode
import xlsxwriter
import pdb

from PIL.Image import Image
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as login_django
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from django.db import connection
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, request, Http404, StreamingHttpResponse
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.utils.six import Module_six_moves_urllib_request
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from board.utils import ab_required
from django.views.static import serve

from board.forms import *
from board.mixins import AjaxableResponseMixin
from board.models import *
from grids import AdvertGrid
from sphinxapi import SphinxClient, SPH_MATCH_EXTENDED2
from realtyboard.settings import STATIC_ROOT, STATICFILES_DIRS, PROJECT_PATH, MEDIA_ROOT
from PIL import Image

import logging
from board.utils import parse_int_str, parse_int

logger = logging.getLogger(__name__)


def yrl(request):
    adverts_list = Advert.objects.all()[:100]
    generation_date = datetime.datetime.now().isoformat()
    return render_to_response('board/yrl_state_feed.xml',
                              {'adverts_list': adverts_list,
                               'generation_date':generation_date},
                               context_instance=RequestContext(request))


def index(request):
    filterform = FilterForm(request.GET)
    filterform.is_valid()
    filterform.clean()
    return render_to_response('index.html', {'filterform': filterform},
                            context_instance=RequestContext(request))


def redirect_url(request, city=None, category=None, title=None, pk=None):
    if category:
        category = category.replace('_', '-')
    if pk:
        url = reverse('advert-detail', kwargs={
            'city': city, 'category': category, 'title': title, 'pk': pk})
    elif category:
        url = reverse('advert-category', kwargs={'city': city, 'category': category})
    elif city:
        url = reverse('advert-city', kwargs={'city': city})

    return redirect(to=url, permanent=True)


def grid_handler(request):
    # handles pagination, sorting and searching
    #grid = AdvertGrid()
    #return HttpResponse(grid.get_json(request), mimetype="application/json")
    page = int(request.GET.get('page', 0)) #  get the requested page
    limit = int(request.GET.get('rows', 50)) #  get how many rows we want to have into the grid
    sidx = request.GET.get('sidx', 'date_of_update') #  get index row - i.e. user click to sort
    sord = request.GET.get('sord', '') #  get the direction
    if sord=='asc':
        sord = ''
    elif sord=='desc':
        sord = '-'

    count = Advert.objects.count()
    total_page = int(ceil(count/limit))

    start = limit*page - limit
    #logger.warn()
    #(page, total_page, start, limit)
    if start < 0:
        start = 0
    rows = []
    for adv in Advert.objects.filter().order_by(sord+sidx)[start:start+limit]:
        rows.append({'id': adv.id,
                    'ceil': adv.sublocality.name if adv.sublocality else '',
                    'rooms_number': adv.rooms_number(),
                    'main_text': adv.main_text,
                    'photo': adv.photo_set.first().preview.url if adv.photo_set.first() else '',
                    'price': adv.price(),
                    'phones': adv.raw_phones,
                    'date_of_update': str(adv.date_of_update)})

    return HttpResponse(json.dumps({'page':str(page),
                                    'total':str(total_page),
                                    'records':count,
                                    'rows':rows}))


def grid_config(request):
    # build a config suitable to pass to jqgrid constructor
    grid = AdvertGrid()
    return HttpResponse(grid.get_config(), mimetype="application/json")


def grid(request):
    filterform = FilterForm(request.GET)
    filterform.is_valid()
    filterform.clean()
    return render_to_response('board/pro_list.html',
                              {'filterform': filterform},
                              context_instance=RequestContext(request))


class AdvertList(ListView):
    model = Advert
    paginate_by = 40
#    search_query = None
    rooms_number = None
    category = None
    city = None
    filterform = None
    cities_list = City.objects.all()

    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        # self.search_query = request.GET.get('text_filter', "")
        if 'city' in kwargs:
            self.city = City.objects.get(slug=kwargs['city'])
        else:
            self.city = self.cities_list.get(id=int(
                request.COOKIES.get('city_id', '20')))
                      
        if 'category' in kwargs:
            self.cat_slag = kwargs['category']
            try:
                self.category = Category.objects.get(slug=self.cat_slag)
            except ObjectDoesNotExist:
                raise Http404
            self.cat_for_seo = self.category
            self.cat_for_seo.description = self.cat_for_seo.description % {
                'name_pr': self.city.name_pr}
            self.cat_for_seo.title = self.cat_for_seo.title % {
                'name': self.city.name, 'name_pr': self.city.name_pr}
            if not self.category.has_parent():
                self.category = Category.objects.filter(parent=self.category.id)
        elif 'city' in kwargs:
            self.cat_for_seo = self.city
        else:
            self.category = None
            self.cat_for_seo = None

        # the some utils for seo
        # if is set query in method get for search, change description seo_text and title
        if self.request.GET.get('text_filter', False):
            seo = Seo.objects.filter(url=self.request.GET.get('text_filter', False)).first()
            if seo:
                self.cat_for_seo = seo
        else:
            #change description seo_text and title if is match in url without domain
            # if 'category' in kwargs:
            seo = Seo.objects.filter(url=self.request.get_full_path()).first()
            if seo:
                self.cat_for_seo = seo

        self.metro_lines = MetroLine.objects.filter(city_id=self.city.id)
        self.big_subloc_list = BigSublocality.objects.filter(
            city_id=self.city.id).order_by('id')
        self.filterform = FilterForm(request.GET, city_object=self.city)
        self.filterform.is_valid()
        self.filterform.clean()
        response = super(ListView, self).get(ListView, request, *args, **kwargs)
        response.set_cookie('city_id', self.city.id)
        return response

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(AdvertList, self).get_context_data(**kwargs)
        # Add in the publisher
        
        context['cat_for_seo'] = self.cat_for_seo
        context['category'] = self.category
        try:
            if self.category.id in [21,22,24]:
                context['category_sdam'] = True
        except AttributeError:
            pass
        context['categories'] = Category.objects.all()
        context['filterform'] = self.filterform
        context['currency'] = self.request.GET.get('currency', '1')
        context['big_subloc_list'] = self.big_subloc_list
        context['metro_lines'] = self.metro_lines
        context['canonical_page'] = int(self.request.GET.get('page', False))
        context['city_h1'] = self.city
        if self.city.id == 8:
            context['city_kiev'] = True
        context['fav_ads'] = ()
        if self.request.user.is_authenticated():
            context['fav_ads'] = self.request.user.favorite_adv.all().values_list('id', flat=True)
        if self.request.user.is_authenticated():
            context['wo_checkbox'] = self.request.user.is_abonent(city_id=self.city.id)
            if self.request.user.is_admin and self.request.GET.get('prozvon', None):
                context['prozvon'] = True
            if self.request.GET.get('woagent') == 'on' and not (
                    self.request.user.is_admin or 
                    self.request.user.is_abonent(city_id=self.city.id)):
                context['wo_disabled'] = u'Поиск без посредников не доступен, оплатите доступ. Показаны все объявления'
        else: 
            context['wo_checkbox'] = False
            if self.request.GET.get('woagent', None) == 'on':
                context['wo_disabled'] = u'Поиск без посредников не доступен, авторизируйтесь на сайте. Показаны все объявления'
        #paid_advert
        if self.category and 'id' in self.category.__dict__ and self.city and not self.request.GET.get('tip', False):
            context['top_advert'] = paid_advert(self, self.city.id, self.category.id, 2)
            context['vip_advert'] = paid_advert(self, self.city.id, self.category.id, 1)
            context['highlight_advert'] = paid_advert_highlight(self, self.city.id, self.category.id, 3)
        #end_paid_advert

        if not self.category and not self.request.GET.get('telefon', False) and not self.request.GET.get('tip', False):
            pre_adv = list(PaidAdvert.objects.filter(advert__author=90,
                    service=1).values_list("advert_id", flat=True).order_by('?')[:6])
            context['vip_advert'] = Advert.objects.filter(id__in=pre_adv)

        if self.request.GET.get('tip', False) == '1':
            context['tip'] = u'Все VIP-объявления'
        elif self.request.GET.get('tip', False) == '2':
            context['tip'] = u'Все ТOP-объявления'

        if self.category:
            context['rooms_filter'] = self.subfilter(
                cat=['kvartiru', 'gostinku', 'dom'])
            context['obj_type_filter'] = self.subfilter(cat=['kommercheskuyu'])
        else:
            context['rooms_filter'] = True
            context['obj_type_filter'] = True
            
        if 'grid' in self.request.path:
            context['all_user_comments'] = ProComment.objects.filter(user=self.request.user)
        return context


    def get_queryset(self):
        """
        TODO: Вот сюда нужно впихнуть все с index'a
        """

                # the some utils for seo
        # if is set query in method get for search, change description seo_text and title
        # if self.request.GET.get('text_filter', False):
        #     seo = Seo.objects.filter(url=self.request.GET.get('text_filter', False)).first()
        #     if seo:
        #         self.cat_for_seo = seo
        # else:
        #     #change description seo_text and title if is match in url without domain
        #     if 'category' in kwargs:
        #         seo = Seo.objects.filter(url=self.request.get_full_path()).first()
        #         if seo:
        #             self.cat_for_seo = seo

        self.url_path = self.request.path

        if self.request.path == '/':
            filter_date = datetime.date.today() - datetime.timedelta(days=3)
            ads = Advert.objects.filter(
                city_id=self.request.COOKIES.get('city_id', 20), is_active=True,
            ).exclude(photo__isnull=True)[:100].prefetch_related('phone_set')
            if len(ads) == 0:
                ads = Advert.objects.filter(city_id=self.request.COOKIES.get('city_id', 20))[:100]
            return ads

        elif 'adverts_with_same_phones' in self.request.path:
            phones = Phone.objects.filter(advert__id=self.kwargs['pk']).prefetch_related('advert')
            ads = []
            for phone in phones:
                ads += phone.advert.all()
            return list(set(ads))

        elif self.request.GET.get('telefon', False):
            telefon = re.sub(r'\D', '', self.request.GET.get('telefon'))
            return Advert.objects.filter(phone__phone=int(telefon), is_active=True)
        elif 'paid_adverts' in self.url_path:
            tip = self.request.GET.get('tip')
            if self.category:
                try:
                    return Advert.objects.filter(paidadvert__service_id=int(tip),
                                             city=self.city, 
                                             category=self.category,
                                             is_active=True)
                except TypeError:
                    return Advert.objects.filter(Q(paidadvert__service_id=1,
                                             city=self.city, 
                                             category=self.category)
                                            |Q(paidadvert__service_id=2,
                                             city=self.city, 
                                             category=self.category))
            else:
                try:
                    return Advert.objects.filter(paidadvert__service_id=int(tip),
                                             city=self.city,
                                             is_active=True)
                except TypeError:
                    return Advert.objects.filter(Q(paidadvert__service_id=1,
                                             city=self.city)
                                            |Q(paidadvert__service_id=2,
                                             city=self.city))

        elif 'similar' in self.url_path:
            subloc = self.request.GET.get('subloc')
            similar = Advert.objects.filter(category=self.category, 
                                            city=self.city)
            if subloc:
                return similar.filter(sublocality__id=subloc)
            else:
                return similar

        elif self.request.GET.get('just_text'):
            text = self.request.GET.get('just_text')
            if re.match(r'^[\d()\s+-]{10,21}$', text):
                text = re.sub(r'\D', '', text)
                return Advert.objects.filter(is_active=True, phone__phone=int(text[-9:]))[:2000]
            if text.isdigit():
                return Advert.objects.filter(is_active=True, id__in=[int(text), int(text[1:])])[:2000]
            # else:
            #     sphinx = SphinxClient()
            #     sphinx.SetMatchMode(SPH_MATCH_EXTENDED2)
            #     sphinx.SetLimits(0, 2000)
            #     ads = sphinx.Query("%s" % text)
            #     # if len(ads['matches']) == 0:
            #     #     return Advert.objects.filter(
            #     #             main_text__icontains=self.request.GET['just_text'])
            #     # else:
            #     ids = [ad['id'] for ad in ads['matches']]
            #     return Advert.objects.filter(id__in=ids)
            else:
                return Advert.objects.filter(is_active=True, main_text__icontains=text)[:2000]
        else:
            result = Advert.objects.filter(is_active=True)
            if self.filterform.cleaned_data.get('text_filter', None):
                # Поиск через стандартные апи сфинкса, ибо православно!
                # sphinx = SphinxClient()
                # sphinx.SetLimits(0, 2000)
                #sphinx.SetMatchMode(SPH_MATCH_EXTENDED2)
                # ads = sphinx.Query("*%s*" % self.filterform.cleaned_data.get('text_filter'))
                # if len(ads['matches']) == 0:
                # result = result.filter(
                #     main_text__icontains=self.filterform.cleaned_data.get('text_filter')
                # )
                text = self.request.GET.get('text_filter')
                if re.match(r'^[\d()\s+-]{10,21}$', text):
                    text = re.sub(r'\D', '', text)
                    return Advert.objects.filter(is_active=True, phone__phone=int(text[-9:]))[:2000]
                if text.isdigit():
                    return Advert.objects.filter(is_active=True, id__in=[int(text), int(text[1:])])[:2000]
                if text.isalpha():
                    result = result.filter(
                    main_text__icontains=self.filterform.cleaned_data.get('text_filter')
                )
                    
                # else:
                #     ids = [ad['id'] for ad in ads['matches']]
                #     logger.info('ids=', ids)
                #     result = result.filter(id__in=ids)
            if '/grid' in self.request.path:
                dark_mark = ProColorMark.objects.filter(user=self.request.user, color='dark').first()
                if dark_mark:
                    dark_ids = list(dark_mark.advert.all().values_list('id', flat=True))
                    dark_by_phone_ids = list(Advert.objects.filter(
                        phone__procolormark=dark_mark).values_list('id', flat=True))
                    result = result.exclude(id__in=list(set(dark_ids+dark_by_phone_ids)))
                
                if self.filterform.cleaned_data.get('hide_show_notes', 0) != 0: 
                    marked_adv_ids = []
                    commented_adv_ids = []
                    
                    if self.filterform.cleaned_data.get('pro_color', None):
                        user_mark_ids = list(ProColorMark.objects.filter(user=self.request.user, 
                            color__in=self.filterform.cleaned_data.get('pro_color')).values_list('id', flat=True))
                        marked_by_phone_adv_ids = list(Advert.objects.filter(
                            phone__procolormark__id__in=user_mark_ids).values_list('id', flat=True))
                        marked_adv_ids = list(Advert.objects.filter(
                            procolormark__id__in=user_mark_ids).values_list('id', flat=True))
                        marked_adv_ids = list(set(marked_by_phone_adv_ids + marked_adv_ids))
                    
                    if self.filterform.cleaned_data.get('pro_comment', None):
                        user_comment_ids = list(ProComment.objects.filter(
                            user=self.request.user).values_list('id', flat=True))
                        commented_by_phone_adv_ids = list(Advert.objects.filter(
                            phone__procomment__id__in=user_comment_ids).values_list('id', flat=True))
                        commented_adv_ids = list(Advert.objects.filter(
                            procomment__id__in=user_comment_ids).values_list('id', flat=True))
                        commented_adv_ids = list(set(commented_by_phone_adv_ids + commented_adv_ids))
                    
                    if self.filterform.cleaned_data.get('hide_show_notes') == 1:
                        result = result.filter(id__in=list(set(marked_adv_ids + commented_adv_ids)))
                    elif self.filterform.cleaned_data.get('hide_show_notes') == 2:
                        result = result.exclude(id__in=list(set(marked_adv_ids + commented_adv_ids)))
                    
            if self.category:
                result = result.filter(category=self.category)
            term_search = self.filterform.cleaned_data.get('term_search', '0')
            
            if int(term_search):
                from_search = datetime.datetime.today()-datetime.timedelta(
                    days=int(term_search))
                result = result.filter(date_of_update__gt=from_search)
            
            if self.filterform.cleaned_data.get('rooms_num', None):
                result = result.prefetch_related('extraflat')
                result = result.filter(extraflat__rooms_number__in=[0] 
                        + ([int(x) for x in self.filterform.cleaned_data['rooms_num']]))
           
            big_subloc_list = self.filterform.cleaned_data.get('bigsubloc', [])
            subloc_list = list(self.filterform.cleaned_data.get('province', []))
            for i, big_subloc in enumerate(self.big_subloc_list):
                subloc_list += list(self.filterform.cleaned_data.get('%ssubloc' % i, []))
            if big_subloc_list:
                subloc_list += Sublocality.objects.filter(
                    big_sublocality__in=big_subloc_list).values_list('id', flat=True)
            subloc_list = list(set(subloc_list))
            metro_list = []
            for i, metro_line in enumerate(self.metro_lines):
                metro_list += list(self.filterform.cleaned_data.get('%smetro_line' % i, []))
            # if subloc_list or big_subloc_list and not metro_list:
            #     result = result.filter(
            #         Q(sublocality__in=subloc_list)
            #         | Q(big_sublocality__in=big_subloc_list)
            #         # | Q(Q(sublocality=None) & Q(big_sublocality=None))
            #         & Q(metro=None))
            # if not metro_list:
            #     result = result.filter(Q(metro=None))

            # if not subloc_list and not big_subloc_list or metro_list:
            #     result = result.filter(
            #         Q(sublocality=None)
            #         & Q(big_sublocality=None)
            #         # | Q(Q(sublocality=None) & Q(big_sublocality=None))
            #         | Q(metro__in=metro_list))

            if subloc_list or big_subloc_list or metro_list:
                if ("9subloc" in self.filterform.cleaned_data) and ("3metro_line" not in self.filterform.cleaned_data):
                    x = [str(x) + 'subloc' for x in range(9)]
                    if set(self.filterform.cleaned_data.keys()) & set(x):
                        result = result.filter(
                            Q(sublocality__in=subloc_list)
                            | Q(big_sublocality__in=big_subloc_list)
                            | Q(Q(sublocality=None) & Q(big_sublocality=None))
                            | Q(metro__in=metro_list))
                    else:
                        result = result.filter(
                            Q(sublocality=None)
                            & Q(big_sublocality=None)
                            | Q(metro__in=metro_list))
                elif ("3metro_line" in self.filterform.cleaned_data) and ("9subloc" not in self.filterform.cleaned_data):
                    x = [str(x) + 'metro_line' for x in range(3)]
                    if set(self.filterform.cleaned_data.keys()) & set(x):
                        result = result.filter(
                            Q(sublocality__in=subloc_list)
                            | Q(big_sublocality__in=big_subloc_list)
                            | Q(metro__in=metro_list)
                            | Q(metro=None))
                    else:
                        result = result.filter(
                            Q(sublocality__in=subloc_list)
                            | Q(big_sublocality__in=big_subloc_list)
                            | Q(metro=None))
                elif ("9subloc" in self.filterform.cleaned_data) and ("3metro_line" in self.filterform.cleaned_data):
                    x = [str(x) + 'subloc' for x in range(9)]
                    y = [str(y) + 'metro_line' for y in range(3)]
                    if set(self.filterform.cleaned_data.keys()) & set(x) or set(self.filterform.cleaned_data.keys()) & set(y):
                        result = result.filter(
                            Q(sublocality__in=subloc_list)
                            | Q(big_sublocality__in=big_subloc_list)
                            | Q(Q(sublocality=None) & Q(big_sublocality=None))
                            | Q(metro__in=metro_list)
                            | Q(metro=None))
                    else:
                        result = result.filter(
                            Q(sublocality=None)
                            & Q(big_sublocality=None)
                            & Q(metro=None))
                else:
                    result = result.filter(
                        Q(sublocality__in=subloc_list)
                        | Q(big_sublocality__in=big_subloc_list)
                        # | Q(Q(sublocality=None) & Q(big_sublocality=None))
                        | Q(metro__in=metro_list))
            if self.filterform.cleaned_data.get('min_price', None):
                if self.filterform.cleaned_data.get('currency') == '1':
                    result = result.filter(
                        price_uah__gte=self.filterform.cleaned_data['min_price'])
                else:
                    result = result.filter(
                        price_usd__gte=self.filterform.cleaned_data['min_price'])
            if self.filterform.cleaned_data.get('max_price', None):
                if self.filterform.cleaned_data.get('currency') == '1':
                    result = result.filter(
                        price_uah__lte=self.filterform.cleaned_data['max_price'])
                else:
                    result = result.filter(
                        price_usd__lte=self.filterform.cleaned_data['max_price'])
            if self.filterform.cleaned_data.get('rent_term', None)\
                and self.filterform.cleaned_data.get('action', None) != 'snimu':
                result = result.prefetch_related('extrarent')
                result = result.filter(
                    Q(extrarent__term=int(self.filterform.cleaned_data['rent_term']))
                    | Q(extrarent__term=None))
            if self.city:
                result = result.filter(city=self.city)
            if len(self.filterform.cleaned_data.get('house_type')) == 1:
                result = result.filter(
                    Q(extrahouse__house_type__in=self.filterform.cleaned_data.get('house_type'))
                    | Q(extrahouse__house_type=None))
            if self.filterform.cleaned_data.get('new_building', None):
                result = result.filter(extraflat__new_building=True)
            if self.filterform.cleaned_data.get('object_type', None):
                result = result.prefetch_related('extracommercial')
                result = result.filter(
                    extracommercial__object_type=self.filterform.cleaned_data['object_type'])
            if self.filterform.cleaned_data.get('sort_level', None):
                if self.filterform.cleaned_data['sort_level'] == '1':
                    level = '-'
                else:
                    level = ''
                result = result.order_by(
                    '%s%s' % (level, self.filterform.cleaned_data['sort_obj']))
            result = result.prefetch_related('phone_set')

            if self.request.user.is_authenticated():
                if self.request.GET.get('prozvon', False) == 'on'\
                    and (self.request.user.is_admin\
                    or self.request.user.is_abonent(city_id=self.city.id)):
                    result = result.exclude(phone__agent__in=[1,2,3,4,5])
                
                elif self.request.GET.get('woagent', False) == 'on'\
                    and (self.request.user.is_admin\
                    or self.request.user.is_abonent(city_id=self.city.id)):
                    result = result.exclude(Q(seller__in=[1,2,5]) |
                                            Q(phone__agent__in=[1,2,5]))
            result = result[:2000]
            result = result.prefetch_related('photo_set', 'city', 'category',
                                             'sublocality', 'metro')
            #pdb.set_trace()
            if self.category:
                try:
                    if str(self.category.id)[1:] in ('1', '2'):
                        result = result.prefetch_related('extraflat')
                    elif str(self.category.id)[1:] == '4':
                        result = result.prefetch_related('extrahouse')
                    elif str(self.category.id)[1:] == '6':
                        result = result.prefetch_related('extralot')
                    elif str(self.category.id)[1:] == '7':
                        result = result.prefetch_related('extracommercial')
                    if str(self.category.id)[:1] == '2':
                        result = result.select_related('extrarent')
                except AttributeError:
                    raise Http404
            else:
                result = result.prefetch_related('extraflat')
            if 'grid' in self.request.path:
                result = result.prefetch_related('procomment_set',
                                                 'procolormark_set',
                                                 'phone_set__procomment_set',
                                                 'phone_set__procolormark_set')

            return result


    def subfilter(self, cat):
        for cat_substr in cat:
            if cat_substr in self.cat_slag:
                return True
        return False


class AdvertDetail(DetailView):
    model = Advert

    def get(self, request, *args, **kwargs):
        cook = request.COOKIES.get('logged_in_status')
        if  kwargs.get('token', None):
            user = UserData.objects.get(token=kwargs.pop('token'))
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login_django(request, user)
        return super(DetailView, self).get(DetailView, request, *args, **kwargs)
         
    def get_queryset(self):
        adv = Advert.objects.filter(id=self.kwargs.get('pk'))#.exclude(is_active=None)
        if not adv or adv[0].is_active == None: # для дебаг режима
            self.template_name = 'board/advert_deleted.html'
        return adv
    # def render_to_response(self, request, **response_kwargs):

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)
        context['qr_code'] = qr_code_for_advert(context['advert'].id, 
                                                self.request.build_absolute_uri())
        
        sim = Advert.objects.filter(category=self.object.category, 
                                    city=self.object.city).exclude(id=self.object.id)
        if self.object.big_sublocality:
            sim = sim.filter(big_sublocality=self.object.big_sublocality)
        if self.object.sublocality:
            sim = sim.filter(sublocality=self.object.sublocality)
        if self.object.metro:
            sim = sim.filter(metro=self.object.metro)
        context['object_list'] = sim[:3]
        
        if str(self.object.category_id)[1:] == '1':
            extra_obj = 'flat'
        elif str(self.object.category_id)[1:] == '2':
            extra_obj = 'room'
        elif str(self.object.category_id)[1:] == '4':
            extra_obj = 'house'
        elif str(self.object.category_id)[1:] == '6':
            extra_obj = 'lot'
        elif str(self.object.category_id)[1:] == '7':
            extra_obj = 'commercial'
        else:
            extra_obj = None
        if str(self.object.category_id)[:1] == '2':
            extra_cat = 'rent'
        else:
            extra_cat = None
        context['extra_obj'] = extra_obj
        context['extra_cat'] = extra_cat
        
        context['special_field'] = (u'Единица измерения',
                                    u'Общая площадь',
                                    u'Новострой',
                                    u'Площадь дома, кв.м',
                                    u'Площадь участка',
                                    u'Период аренды',
                                    u'Состояние',
                                    u'Тип',
                                    u'Этаж',
                                    u'Этажность')
        
        banners = PaidBanner.objects.filter(place__in=(11, 12, 13), 
                                            city_id=kwargs['object'].city,
                                            expiration_date__gte=datetime.date.today())
        context['banners'] = {}
        for banner in banners:
            context['banners'][banner.place] = banner
        return context


@csrf_protect
def advert_create(request):
    category_id = request.GET.get('cat_id', request.POST.get('cat_id', 0))
    city_id = request.COOKIES.get('city_id', 20)
    if request.method == "POST":
        spam_words = SpamWord.objects.all()
        phone = re.sub(r'\s|\(|\)|\-','', request.POST['raw_phones'])
        for sw in spam_words:
            if sw.word in request.POST['main_text']:
                return render(request, 'message.html',
                              {'message': u'Ваше объявление заблокировано за спам.'})
            elif sw.word in request.POST['title']:
                return render(request, 'message.html', 
                              {'message': u'Ваше объявление заблокировано за спам.'})
            elif sw.word in phone:
                return render(request, 'message.html', 
                              {'message': u'Ваше объявление заблокировано за спам.'})
        if request.POST.get('mail', '') != '':
            # seems this is a bot
            return redirect(reverse_lazy('board-main'))
        else:
            advform = AdvertForm(data=request.POST)
            fastuserform = FastUserForm(data=request.POST)
            extraforms = get_extra_model(category_id=category_id, data=request.POST)
            context = {'advform': advform,
                       'extraforms': extraforms}
            if not request.user.is_authenticated():
                context['fastuserform'] = fastuserform
            mark = False
            if advform.is_valid() and request.user.is_authenticated():
                adv = advform.save()
                adv.author = request.user
                mark = True
                request.user.send_mail(9)
            elif advform.is_valid():
                user = get_user_by('email', request.POST['email'])
                if user:
                    adv = advform.save()
                    adv.author = user
                    mark = True
                    user.send_mail(9)
                elif fastuserform.is_valid():
                    user_pass = generate_pass(5)
                    user = UserData.objects.create_user(email=request.POST['email'],
                                                        username=request.POST['email'],
                                                        password=user_pass,
                                                        first_name = request.POST['first_name'])
                    user.remember = user_pass
                    adv = advform.save()
                    user.save()
                    adv.author = user
                    mail_text = u"""Вы успешно разместили объявление на сайте ci.ua. Ваше объявление 
                        доступно вам для редактирования по ссылке http://ci.ua/accounts/profile/\n
                        Данные для доступа к объявлению на ci.ua:\n
                        Ваш логин: %s\n
                        Ваш пароль: %s\n""" % (request.POST['email'], user_pass)
                    send_mail(u"Вы опубликовали объявление на ci.ua",
                              mail_text, 'noreply@ci.ua', [request.POST['email']], fail_silently=True)
                    mark = True
            if mark:
                adv.save()
                if extra_valid(extraforms):
                    extra_save(extraforms, adv)
                else:
                    advform = AdvertForm()
                    extraforms = get_extra_model(category_id)

                for i, key in enumerate(sorted(request.FILES.keys())):
                    img = request.FILES[key]
                    img.name = img.name.encode('utf-8')
                    photo = Photo()
                    photo.advert = adv
                    photo.order = i
                    photo.photo.save(
                        "%s.%s" % (md5(img.name).hexdigest(),
                                   re.search(r'[a-zA-Z]+$', img.name).group()),
                        ContentFile(img.read())
                    )
                    photo.save()
                return redirect(adv.get_absolute_url())
    else:
        context = {'advform': AdvertForm(),
                   'extraforms': get_extra_model(category_id)}
        if not request.user.is_authenticated():
            context['fastuserform'] = FastUserForm()
    response = render_to_response(
        'board/advert_form.html', context, context_instance=RequestContext(request))
    return response


def get_extra_form(request):
    cat_id = request.GET.get('cat_id', 0)
    advert = request.GET.get('adv_id', None)
    if advert:
        forms = get_extra_model(0, None, Advert.objects.get(id=advert))
    else:
        forms = get_extra_model(cat_id, None)
    return HttpResponse("".join([x.as_div() for x in forms]))


def get_sublocality(request):
    city_id = request.GET.get('city_id', 0)
    sublocality_id = request.GET.get('id_sublocality', False)
    if sublocality_id:
        slug = City.objects.get(id=sublocality_id).slug
        return HttpResponse(json.dumps({'slug':slug}))
    big_subloc_list = BigSublocality.objects.filter(city=city_id)
    result = {}
    result['big_subloc'] = [model_to_dict(x) for x in
                            BigSublocality.objects.filter(city=city_id)]
    result['adminsub'] = [model_to_dict(x) for x in
                          Sublocality.objects.filter(city=city_id)]
    result['metro_line'] = [model_to_dict(x) for x in
                            MetroLine.objects.filter(city=city_id)]
    result['metro'] = [model_to_dict(x) for x in
                       Metro.objects.filter(city=city_id)]
    return HttpResponse(json.dumps(result))


def image_remove(request):
    try:
        photo_id = request.GET.get('id')
        result = {"result": Photo.objects.get(id=photo_id).delete()}
    except Exception, ex:
        result = {"result": ex}
    return HttpResponse(json.dumps(result))


def advert_update(request, pk):
    advert = Advert.objects.get(id=pk)
    if request.user.is_admin or advert.author == request.user:
        category_id = request.GET.get('cat_id', 0)
        if request.method == "POST":
            advform = AdvertForm(data=request.POST, instance=advert)
            extraforms = get_extra_model(category_id=category_id, data=request.POST)
            if advform.is_valid():
                adv = advform.save()
                adv.save()
                extraforms = get_extra_model(0, data=request.POST, advert=adv)
                if extra_valid(extraforms):
                    extra_save(extraforms, adv)
                else:
                    advform = AdvertForm(model_to_dict(advert))
                    extraforms = get_extra_model(category_id, advert=advert)
                
                for key in request.FILES:
                    img = request.FILES[key]
                    img.name = img.name.encode('utf-8')
                    photo = Photo()
                    photo.advert = adv
                    photo.order = int(re.sub(r'\D', '', key) or '0')
                    photo.photo.save("%s.%s" % (
                            md5(img.name).hexdigest(),
                            re.search(r'[a-zA-Z]+$', img.name).group()
                        ),
                        ContentFile(img.read())
                    )
                    photo.save()
                photos = Photo.objects.filter(advert=adv)
                img_order = request.POST['img_order'].split(';')
                for i, val in enumerate(img_order):
                    if val:
                        img_order[i] = val.split(',')
                        for phot in photos:
                            if (img_order[i][1] in phot.photo.name):
                                phot.order = img_order[i][0]
                                phot.save()
                return redirect(adv.get_absolute_url())
        else:
            advform = AdvertForm(model_to_dict(advert))
            extraforms = get_extra_model(category_id, advert=advert)
    else:
        return HttpResponse("You don't have permision to update this advert", status=403)

    return render_to_response('board/advert_form.html', {
        'advform':advform,
        'extraforms':extraforms,
        'images':advert.photo_set.all()
    }, context_instance=RequestContext(request))


def check_phone(request):
        phone = request.GET.get('telefon', '')
        conclusion = None
        title = 'Проверка телефона на посредника'
        if request.GET.get('version', '') == '1':
            title = '('+phone[:3]+')'+phone[3:5]+'-'+phone[5:7]+'-'+phone[7:]
            level_up = 2
        elif request.GET.get('version', '') == '2':
            conclusion = Phone.objects.filter(
                phone=int(re.sub(r'\D', '', phone))).first()
            if conclusion in Phone.objects.filter(Q(agent=1)|Q(agent=2)):
                conclusion = conclusion
            else:
                conclusion = None
            level_up = 3
            title = phone[:3]+' '+phone[3:5]+' '+phone[5:7]+' '+phone[7:]
            phone = re.sub(r'/\D/', '', phone)
        else:
            level_up = 1
        return render_to_response('board/check_phone.html', {
        'level_up': level_up,
        'phone': phone,
        'title': title,
        'conclusion': conclusion
    }, context_instance=RequestContext(request))


def advert_up(request, pk):  # поднималка объявления
    if request.is_ajax():
        adv = Advert.objects.get(pk=pk)
        if not adv.is_active:
            adv.is_active = True
            if adv.up_available():
                adv.date_of_update = timezone.now()
            adv.save()
            return HttpResponse(u';Объявление №%s опубликовано.' % adv.id)
        if adv.up_available():
            adv.date_of_update = timezone.now()
        else:
            return HttpResponse(u'Обновление даты для этого объявления еще не доступно')
        adv.save()
        current_time = datetime.datetime.now();
        return HttpResponse(u'%s в %s;Объявление №%s успешно обновлено.' % (
            current_time.strftime("%d.%m.%y"), current_time.strftime("%H:%M"), pk))
    else:
        return HttpResponse(u'Ошибка! Объявление №%s не обновлено' % pk)


def advert_deactivate(request, pk):  # отправка объявления в черновики
    if request.is_ajax():
        adv = Advert.objects.get(pk=pk)
        if adv.author != request.user:
            return HttpResponse(u"Доступ закрыт", status=403)
        adv.is_active = False
        adv.save()
        return HttpResponse(u'Объявление №%s больше не публикуется на доске.' % pk)
    else:
        return HttpResponse(u'Ошибка, объявление №%s все еще активно' % pk)

def add_to_fav(request):
    if request.is_ajax and request.method == 'POST':
        adv = Advert.objects.get(id=request.POST.get('id'));
        if request.user == adv.author:
            return HttpResponse(json.dumps({
                'message':u'Нельзя добавлять свои объявления!',
                'result':'not_done'
            }))
        adv.userdata_set.add(request.user);
        return HttpResponse(json.dumps({
            'message':u'Объявление добавлено в ваш блокнот.',
            'result':'success'
        }))
    return render(request, 'message.html', {'message': u'Неверный запрос'})

def remove_from_fav(request):  # удаление из избранных
    if request.is_ajax() and request.method == 'POST':
        adv = Advert.objects.get(pk=int(request.POST.get('id')))
        adv.userdata_set.remove(request.user)
        return HttpResponse(json.dumps({
            'message': u'Объявление убрано из вашего блокнота.',
            'result': 'success'}))
    render('message.html', {'message': u'Неверный запрос.'})

class AdvertDelete(AjaxableResponseMixin, DeleteView):
    model = Advert
    success_url = reverse_lazy('property-list')

def advert_to_delete(request, pk):  # удаление объявления
    if request.is_ajax():
        adv = Advert.objects.get(pk=pk)
        if request.user.is_admin or request.user == adv.author:
            adv.is_active = None
            adv.save()
            AdvertToDelete.objects.get_or_create(advert=adv)
            return HttpResponse(u'Объявление отмечено на удаление, оно будет храниться\
                 в удаленных в течение недели.')
        else:
            return HttpResponse(u"У вас нет прав доступа", status=403)
    if request.user.is_admin:
        adv = Advert.objects.get(pk=pk)
        adv.is_active = None
        adv.save()
        AdvertToDelete.objects.get_or_create(advert=adv)
        return render(request, 'message.html', {'message': u'Объявление отмечено на\
            удаление, оно будет храниться в удаленных в течение недели.'})
    else:
        return render(request, 'message.html', {'message': u'Неверный запрос'})

def advert_recover(request):
    if request.is_ajax():
        if request.method == 'POST':
            adv = Advert.objects.get(id=request.POST.get('id'))
            if adv.author != request.user:
                return HttpResponse(u'У вас нет прав доступа', status=403)
            adv.is_active = True
            adv.save()
            del_obj = AdvertToDelete.objects.get(advert_id=adv.id)
            del_obj.delete()
            return HttpResponse(u'Объявление восстановлено')
    return HttpResponse(u"У вас нет прав доступа", status=403)

def other(request, other):
    return redirect(to='/', permanent=True)
    return HttpResponse(u'ссылка не найдена', status=404)


@ab_required
def filetree(request, city):

    # current = request.GET.get('city_data', False)

    current_name_of_city = City.objects.get(slug=city) if city else 'kharkov'

    if city == 'kiev':
        # path ='/data/web/media/uploads/base_files/rar/kiev/%s/' % datetime.datetime.now().year
        path = os.path.join(settings.BAZADIR, city ,request.GET.get('path', '2015'))
        # print 'os.path', path
        if os.path.exists(path):
            os.chdir(path)
            dirlist = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.basename)
            dirlist.reverse()
        else:
            dirlist = []
    elif city == 'kharkov':
        path = os.path.join(settings.BAZADIR, city ,request.GET.get('path', '2015'))
        # path = '/data/web/media/bazadocumets/2015/'
        if os.path.exists(path):
            os.chdir(path)
            dirlist = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.basename)
            dirlist.reverse()
        else:
            dirlist = []
    else:
        path = os.path.join(settings.BAZADIR, request.GET.get('path', '2015'))
        if os.path.exists(path):
            os.chdir(path)
            dirlist = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.basename)
            dirlist.reverse()
        else:
            dirlist = []


    return render_to_response('flist.html', {'dirlist': dirlist,
        'path': request.GET.get('path', '2015'),
        'current': city,
        'current_name_of_city':current_name_of_city,
        },
        context_instance=RequestContext(request))
# Special


def stats_parser(request, city=None, data=None):
    if city is not None:
        date = StatAdvert.objects.only("creation_date")
        date_all = []
        for i in date:
            date_all.append(i.creation_date)
        list_date = date_all[::18]
        list_date = list_date[::-1]
    data_act = re.findall(r'\d+\-\d+\-\d+', data)
    source_olx = []
    source_domik = []
    source_premier = []
    source_domria = []
    source_md = []
    source_fn = []
    source_mirkvartir= []
    source_realt = []
    source_aviso = []
    source= []
    if data_act:
        city = City.objects.get(slug=city)
        date = StatAdvert.objects.filter(city_id=city, creation_date = data)
        for i in date:
            source.append(i.source)
            source.append(i.prodam_kvartiru)
            source.append(i.prodam_komnatu) 
            source.append(i.prodam_dom) 
            source.append(i.prodam_uchastok) 
            source.append(i.prodam_nedvizhimost) 
            source.append(i.sdam_kvartiru)
            source.append(i.sdam_komnatu) 
            source.append(i.sdam_dom) 
            source.append(i.sdam_uchastok) 
            source.append(i.sdam_nedvizhimost)
        source_olx = source[0:11]
        source_domik = source[11:22]
        source_premier = source[22:33]
        source_domria = source[33:44]
        source_md = source[44:55]
        source_fn = source[55:66]
        source_mirkvartir = source[66:77]
        source_realt = source[77:88]
        source_aviso = source[88:99]
    return render_to_response('board/advert_stats.html',{
        'list_date':list_date,
        'source_olx':source_olx,
        'source_domik':source_domik,
        'source_premier':source_premier,
        'source_domria':source_domria,
        'source_md':source_md,
        'source_fn':source_fn,
        'source_mirkvartir':source_mirkvartir,
        'source_realt':source_realt,
        'source_aviso':source_aviso,
        },
        context_instance=RequestContext(request))

def set_city(request):
    if request.is_ajax():
        if request.method == 'POST':
            chosen_city_id = request.POST.get('chosen_city_id')
            response = HttpResponse('1')
            response.set_cookie('city_id', chosen_city_id)
            return response

def add_to_agent(request):
    if request.is_ajax() and request.user.is_admin:
        for phone in Phone.objects.filter(advert__id__in=[request.POST['adv_id']]):
            phone.agent = 1
            phone.save()
        return HttpResponse(json.dumps(
            {'status': 'done', 'message': u'Телефоны отмечены, как агентсие'}))

def add_to_owner(request):
    if request.is_ajax() and request.user.is_admin:
        for phone in Phone.objects.filter(advert__id__in=[request.POST['adv_id']]):
            phone.agent = 4
            phone.save()
        return HttpResponse(json.dumps({'status': 'done'}))
    
def add_to_unknown(request):
    if request.is_ajax() and request.user.is_admin:
        for phone in Phone.objects.filter(advert__id__in=[request.POST['adv_id']]):
            phone.agent = None
            phone.save()
        return HttpResponse(json.dumps({'status': 'done'}))

def del_all_advert(request):
    if request.is_ajax() and request.user.is_admin:
        for phone in Phone.objects.filter(advert__id__in=[request.POST['adv_id']]):
            a = Advert.objects.filter(phone__phone=str(phone)).delete()
            print a 
        return HttpResponse(json.dumps({'status': 'done'}))

def add_to_spam(request):
    if request.is_ajax() and request.user.is_admin:
        advert = Advert.objects.get(id=request.POST['adv_id'])
        advert.is_active = False
        advert.save()
        return HttpResponse(json.dumps({'status': 'done'}))
        
def poll(request):
    if request.user.is_authenticated():
        advert_id = request.POST.get('advert_id', 0)
        phones = Phone.objects.filter(advert__id=advert_id)
        mes = '<div>Спасибо:</div>'
        for phone in phones:
            # if not Choice.objects.filter(ip=request.META.get('REMOTE_ADDR'), user=request.user, phone=phone):
            if not Choice.objects.filter(user=request.user, phone=phone):
                choice = Choice()
                choice.choice_text = request.POST.get('comment', 0)
                choice.ip = request.META.get('REMOTE_ADDR')
                choice.poll = Poll.objects.get(id=request.POST.get('poll'))
                choice.phone = phone
                choice.advert = Advert.objects.get(id=advert_id)
                choice.user = request.user
                choice.save()

                if Choice.objects.filter(phone=phone).count() > 7:
                    phone.agent = 1
                    try:
                        phone.save()
                    except Exception, ex:
                        print ex

                mes += '<div style="color: limegreen;" >Номер 0%s добавлен на модерацию!!! </div>' % phone.phone
            else:
                mes += '<div style="color: red;" >Номер 0%s уже был вами добавлен!!! </div>' % phone.phone
        return HttpResponse(mes)
        # return HttpResponse('<span style="color: limegreen;" >Спасибо, информация отправлена на модерацию!</span>')
    else:
        return HttpResponse('Только для пользователей оплативших " Базу без посредников" !')


def paid_advert(self, paid_city, paid_category, service):
    page = self.request.GET.get('page', False)
    cdv = 6
    if int(page) == 0 or int(page) >= 1:
        if  service == 2: # top
            if int(page) == 0 or int(page) == 1:
                cdv = 5
            else:
                cdv = 3
        if service == 5: # vip
            if int(page) == 0 or int(page) == 1:
                cdv = 6
            else:
                cdv = 3
    # advert = []
    #
    # if self.category.id == 16:
    #     advert = Advert.objects.filter(id__in=[18795, 25383, 58297, 25065, 44398, 5889])
    # else:
    pre_adv = list(PaidAdvert.objects.filter(
        advert__category=paid_category,
        advert__city=paid_city,
        service=service).values_list("advert_id", flat=True).order_by('?')[:cdv])  # 6 random results.
    advert = Advert.objects.filter(id__in=pre_adv)
    if self.request.path == '/':
        advert = Advert.objects.filter(id__in=[18795, 25383, 58297, 25065, 44398, 5889])
    return advert

def paid_advert_highlight(self, paid_city, paid_category, service):
    advert = list(PaidAdvert.objects.filter(
        advert__category=paid_category,
        advert__city=paid_city,
        service=service).values_list("advert_id", flat=True))
    return advert
    
    
def get_user_by(field, value):
    try:
        if field == 'email':
            user = UserData.objects.get(email=value)
        elif field == 'username':
            user = UserData.objects.get(username=value)
    except:
        user = None
    return user
    

def generate_pass(lenth=6):
    string = "AaBb0CcDd1EeFf2GgHh3IiJj4KkLl5MmNn6OoPp7QqRr8SsTt9UuVvXxYyZz"
    pas = ''
    for i in range(lenth):
        pas += random.choice(string)
    return pas

def qr_code_for_advert(id_adv, path):
    img = qrcode.make(path)
    dj_path = '/static/QR-code_images_for_adverts/%s.png' % id_adv
    gen_path = os.path.join(PROJECT_PATH, dj_path[1:])
    if not os.path.exists(gen_path):
        img.save(gen_path)
        return dj_path
    else:
        return dj_path
    
def add_pro_comment(request):
    if request.is_ajax() and request.method == 'POST':
        adv = Advert.objects.get(id=request.POST['adv_id'])
        try:
            pro_comment = ProComment.objects.get(user=request.user, 
                                                 text=request.POST['text'])
        except ProComment.DoesNotExist:
            pro_comment = ProComment.objects.create(user=request.user, 
                                                    text=request.POST['text'])
        if request.POST['on_phone'] == 'true':
            phones = adv.phone_set.all()
            for phone in phones:
                phone.add_pro_comment(user=request.user,
                                      pro_comment=pro_comment)
        else:
            adv.add_pro_comment(user=request.user, pro_comment=pro_comment)
        return HttpResponse(json.dumps({'status': 'done', 'comment_id': pro_comment.id,
                            'text': pro_comment.text}))
        
def remove_pro_comment(request):
    if request.is_ajax() and request.method == 'POST':
        comment = ProComment.objects.get(id=request.POST['comment_id'], user=request.user)
        adv = Advert.objects.get(id=request.POST['obj_id']);
        if request.POST['on_phone'] == 'true':
            phones = adv.phone_set.all()
            for phone in phones:
                comment.phone.remove(phone)
        else:
            comment.advert.remove(adv)      
        return HttpResponse(json.dumps({'status': 'done'}))
        
def add_pro_color_mark(request):
    if request.is_ajax() and request.method == 'POST':
        adv = Advert.objects.get(id=request.POST['adv_id'])
        try:
            color_mark = ProColorMark.objects.get(user=request.user, 
                                                  color=request.POST['color'])
        except ProColorMark.DoesNotExist:
            color_mark = ProColorMark.objects.create(user=request.user, 
                                                     color=request.POST['color'])
        if request.POST['on_phone'] == 'true':
            phones = adv.phone_set.all()
            for phone in phones:
                phone.add_pro_color_mark(user=request.user,
                                         color_mark=color_mark)
        else:
            adv.add_pro_color_mark(user=request.user,
                                       color_mark=color_mark)
        return HttpResponse(json.dumps({'status': 'done'}))
        
def remove_pro_color_mark(request):
    if request.is_ajax() and request.method == 'POST':
        adv = Advert.objects.get(id=request.POST['adv_id'])
        if request.POST['on_phone'] == 'true':
            phones = adv.phone_set.all()
            for phone in phones:
                try:
                    phone.procolormark_set.get(user=request.user).phone.remove(phone)
                except ProColorMark.DoesNotExist:
                    pass
        else:        
            adv.procolormark_set.get(user=request.user).advert.remove(adv)
        return HttpResponse(json.dumps({'status': 'done'}))
        

def get_complaint(request):
    if request.is_ajax() and request.method == 'POST':
        data = json.loads(request.POST.get('complaint'), encoding='utf-8')
        complaint = Complaint.objects.create(advert_id=int(data['advert_id']),
                                             email=data['user_email'],
                                             reason=data['reason'])
        user_id = parse_int(data['user_id'])
        if user_id:
            complaint.user_id = user_id
        for phone in Phone.objects.filter(advert__id=int(data['advert_id'])):
            complaint.phones.add(phone)
        complaint.save()
        return HttpResponse('complaint on advert ' + data['advert_id'] + 'have been saved')

def save_txt(request):
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/txt')
    os.system('rm -r %s/*' % temp_dir) 
    os.system('touch %s/%s' % (temp_dir,'ciua_txt.txt')) 
    advert_all = Advert.objects.filter(city_id=20).order_by('-date_of_update')[:200]
    source_file = open('%s/%s' % (temp_dir, 'ciua_txt.txt'),'w') 
    for i in advert_all:
        source_file.write('Код- ')
        source_file.write(str(i.id))
        source_file.write(' ')
        if i.sublocality:
            sub = str(i.sublocality)
            source_file.write(sub)
            source_file.write(' ')
        if i.main_text:
            text = i.main_text[:180].encode('utf8')
            source_file.write(text)
            source_file.write(' ')
        if i.price_uah:
            source_file.write('Цена- ')
            source_file.write(str(i.price_uah))
            source_file.write(' ')
        if i.raw_phones:
            source_file.write('Телефон- ')
            source_file.write(str(i.raw_phones))
        source_file.write('.'+ '\r\n')
    source_file.close()
    os.system('rar a -ep1 %s/base_files/txt/save_chast.rar  %s/ciua_txt.txt' % (MEDIA_ROOT, temp_dir)) 
    filepath = ('%s/%s' % (temp_dir, 'save_chast.rar')) 
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

def save_city_txt(request, city, category):
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/txt')
    os.system('rm -r %s/*' % temp_dir) 
    os.system('touch %s/%s' % (temp_dir,'ciua_txt.txt')) 
    city_adv = City.objects.get(slug=city)
    category_adv = Category.objects.get(slug=category)
    advert_all = Advert.objects.filter(city=city_adv, category=category_adv).order_by('-date_of_update')[:200]
    source_file = open('%s/%s' % (temp_dir, 'ciua_txt.txt'),'w') 
    for i in advert_all:
        source_file.write('Код- ')
        source_file.write(str(i.id))
        source_file.write(' ')
        if i.sublocality:
            sub = str(i.sublocality)
            source_file.write(sub)
            source_file.write(' ')
        if i.main_text:
            text = i.main_text[:180].encode('utf8')
            source_file.write(text)
            source_file.write(' ')
        if i.price_uah:
            source_file.write('Цена- ')
            source_file.write(str(i.price_uah))
            source_file.write(' ')
        if i.raw_phones:
            source_file.write('Телефон- ')
            source_file.write(str(i.raw_phones))
        source_file.write('.'+ '\r\n')
    source_file.close()
    os.system('rar a -ep1 %s/base_files/txt/save_chast.rar  %s/ciua_txt.txt' % (MEDIA_ROOT, temp_dir)) 
    filepath = ('%s/%s' % (temp_dir, 'save_chast.rar')) 
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

def save_xls(request):
    """Очистка папки"""
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/xls')
    os.system('rm -r %s/*' % temp_dir) 

    """Создание/открытие"""
    workbook = xlsxwriter.Workbook('%s/%s' % (temp_dir,'ciua_xls.xls'))
    worksheet = workbook.add_worksheet()
    advert_all = Advert.objects.filter(city_id=20).order_by('-date_of_update')[:1000]

    """Формат"""
    format_title = workbook.add_format({'bold': True})
    format_title.set_align('center')
    format_phone = workbook.add_format()
    format_phone.set_text_wrap()
    format_phone.set_align('bottom')
    format_phone.set_align('center')
    format_text = workbook.add_format()
    format_text.set_align('vjustify')
    url_format = workbook.add_format({
        'font_color': 'blue',
        'underline':  1
        })
    url_format.set_align('center')
    url_format.set_align('vcenter')
    
    """Колонки"""
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 19)
    worksheet.set_column('C:C', 75)
    worksheet.set_column('D:D', 10)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 21)

    
    rows = 1
    while rows <= 1000:
        worksheet.set_row(rows, 45)
        rows = rows + 1
    """Вершина"""
    worksheet.write('A1', u'Код', format_title)
    worksheet.write('B1', u'Район', format_title)
    worksheet.write('C1', u'Текст', format_title)
    worksheet.write('D1', u'Цена грн.', format_title)
    worksheet.write('E1', u'Телефон', format_title)
    worksheet.write('F1', u'Ссылка', format_title)

    """Обьявления"""
    row = 1
    col = 0
    for i in advert_all:
        worksheet.write(row , col, i.id)
        if i.sublocality:
            sub = str(i.sublocality).decode('utf8')
            worksheet.write(row, col+1, sub)
        else:    
            worksheet.write(row, col+1, ' ')
        if i.main_text:
            text = i.main_text[:180]
            worksheet.write(row, col+2, text, format_text )
        else:
            worksheet.write(row, col+2, ' ')
        if i.price_uah:
            worksheet.write(row, col+3, i.price_uah)
        else:
            worksheet.write(row, col+3, ' ')
        if i.raw_phones: 
            phone = re.sub(r'\s|\(|\)|\-','', i.raw_phones)
            worksheet.write(row, col+4, phone, format_phone)
        else:
            worksheet.write(row, col+4, ' ')
        w = City.objects.get(advert=i)
        e = Category.objects.get(advert=i)
        text = 'http://ci.ua/'+w.slug+'/'+e.slug+'/'+i.slug + '/'+ unicode(i.id)
        worksheet.write_url(row, col+5, text , url_format, u'Объявление на сайте')
        row += 1
    """Закрытие/Загрузка"""
    workbook.close()
    filepath = ('%s/%s' % (temp_dir, 'ciua_xls.xls')) 
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

def save_city_xls(request, city, category):
    """Очистка папки"""
    temp_dir = os.path.join(MEDIA_ROOT, 'base_files/xls')
    os.system('rm -r %s/*' % temp_dir) 

    """Создание/открытие"""
    workbook = xlsxwriter.Workbook('%s/%s' % (temp_dir,'ciua_xls.xls'))
    worksheet = workbook.add_worksheet()
    city_adv = City.objects.get(slug=city)
    category_adv = Category.objects.get(slug=category)
    advert_all = Advert.objects.filter(city=city_adv, category=category_adv).order_by('-date_of_update')[:1000]

    """Формат"""
    format_title = workbook.add_format({'bold': True})
    format_title.set_align('center')
    format_phone = workbook.add_format()
    format_phone.set_text_wrap()
    format_phone.set_align('bottom')
    format_phone.set_align('center')
    format_text = workbook.add_format()
    format_text.set_align('vjustify')
    url_format = workbook.add_format({
        'font_color': 'blue',
        'underline':  1
        })
    url_format.set_align('center')
    url_format.set_align('vcenter')
    
    """Колонки"""
    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 19)
    worksheet.set_column('C:C', 75)
    worksheet.set_column('D:D', 10)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 21)

    
    rows = 1
    while rows <= 1000:
        worksheet.set_row(rows, 45)
        rows = rows + 1
    """Вершина"""
    worksheet.write('A1', u'Код', format_title)
    worksheet.write('B1', u'Район', format_title)
    worksheet.write('C1', u'Текст', format_title)
    worksheet.write('D1', u'Цена грн.', format_title)
    worksheet.write('E1', u'Телефон', format_title)
    worksheet.write('F1', u'Ссылка', format_title)

    """Обьявления"""
    row = 1
    col = 0
    for i in advert_all:
        worksheet.write(row , col, i.id)
        if i.sublocality:
            sub = str(i.sublocality).decode('utf8')
            worksheet.write(row, col+1, sub)
        else:    
            worksheet.write(row, col+1, ' ')
        if i.main_text:
            text = i.main_text[:180]
            worksheet.write(row, col+2, text, format_text )
        else:
            worksheet.write(row, col+2, ' ')
        if i.price_uah:
            worksheet.write(row, col+3, i.price_uah)
        else:
            worksheet.write(row, col+3, ' ')
        if i.raw_phones: 
            phone = re.sub(r'\s|\(|\)|\-','', i.raw_phones)
            worksheet.write(row, col+4, phone, format_phone)
        else:
            worksheet.write(row, col+4, ' ')
        w = City.objects.get(advert=i)
        e = Category.objects.get(advert=i)
        text = 'http://ci.ua/'+w.slug+'/'+e.slug+'/'+i.slug + '/'+ unicode(i.id)
        worksheet.write_url(row, col+5, text , url_format, u'Объявление на сайте')
        row += 1
    """Закрытие/Загрузка"""
    workbook.close()
    filepath = ('%s/%s' % (temp_dir, 'ciua_xls.xls')) 
    return serve(request, os.path.basename(filepath), os.path.dirname(filepath))

def feed_kiev(request):
    temp_dir = os.path.join(PROJECT_PATH)
    file_path = os.path.join(temp_dir ,'templates/feed_ciua_kiev.xml')
    return render(request,file_path ,content_type='application/xml')

def feed_kharkov(request):
    temp_dir = os.path.join(PROJECT_PATH)
    file_path = os.path.join(temp_dir ,'templates/feed_ciua_kharkov.xml')
    return render(request,file_path ,content_type='application/xml')