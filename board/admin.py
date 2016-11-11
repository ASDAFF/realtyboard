# -*- coding: utf-8 -*-
from board import models as board_models
from django.conf.urls import patterns
from django.contrib import admin
from django.db.models.base import ModelBase
from django.shortcuts import render

from board.models import *
from personal.models import UserIP, UserData, UserPayment, PaidService


# python magic don't try to understand!
class PhoneAdmin(admin.ModelAdmin):
    list_display = ('phone', 'owner', 'agent', 'date_of_addition',)
    search_fields = ['phone']
    list_filter = ['agent']
    fields = ['owner', 'phone', 'agent']
    radio_fields = {'agent': admin.VERTICAL}


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('advert', 'image_tag', 'alt')
    readonly_fields = ('image_tag',)


class UserDataAdmin(admin.ModelAdmin):
    fields = ['id', 'username', 'is_active', 'creation_date', 'counting_logins',
              'first_name', 'last_name', 'email', 'remember', 'groups', 'current_balance']
    list_display = ('username', 'id', 'get_full_name', 'email', 'active_cities',
                    'creation_date', 'current_balance',)
    readonly_fields = ['id',  'is_abonent', 'creation_date',  'first_name', 
                       'last_name', 'counting_logins', 'remember',]
    search_fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                     'remember', 'memoirs']
    list_filter = ['groups', 'services']
    ordering = ['username']

    def change_view(self, request, object_id, extra_context={}):
        user_obj = UserData.objects.get(id=object_id)
        extra_context['user_ips'] = user_obj.get_user_ips()
        extra_context['ab_operations'] = user_obj.get_ab_op()
        extra_context['phone_list'] = user_obj.get_phones()
        extra_context['available_bases'] = PaidService.objects.filter(
            name__startswith='base_')
        extra_context['active_bases'] = user_obj.services.all()
        return super(UserDataAdmin, self).change_view(request, object_id,
                                                extra_context=extra_context)

    class Media:
        js = ("/static/js/jquery-2.1.0.js",
              "/static/admin/js/admin_user.js",)
        css = {'all': ("/static/admin/css/admin_user.css",)}
        
    
class PhotoInline(admin.TabularInline):
    model = Photo
    readonly_fields = ('image_tag', 'id')
    extra = 3

class PollInline(admin.TabularInline):
    model = Poll
    readonly_fields = ('question', 'id')
    # extra = 3


class ChoiceAdmin (admin.ModelAdmin):
    list_display = ['choice_text', 'phone', 'pub_date', 'advert']
    list_filter = ['ip', 'poll']
    readonly_fields = ['phone', 'user', 'advert']
    search_fields = ['id', 'choice_text', 'phone__phone']


class AdvertAdmin (admin.ModelAdmin):
    list_display = ['id', 'category', 'city', 'date_of_update']
    list_filter = ['city', 'category']
    search_fields = ['id', 'main_text', 'author__username']
    inlines = [PhotoInline]

    def get_urls(self):
        urls = super(AdvertAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^my_view/$', self.admin_site.admin_view(self.my_view))
        )
        return my_urls + urls

    def my_view(self, request):
        # custom view which should return an HttpResponse
        data=None
        return render(request, 'board/templates/board/my_view.html', {'data': data})


class CategoryAdmin (admin.ModelAdmin):
    list_display = ['name', 'slug', 'title', 'seo_text']
    search_fields = ['slug', 'name', "title"]


class CityAdmin (admin.ModelAdmin):
    list_display = ['name', 'slug', 'title']
    search_fields = ['slug', 'name', "title"]

class SeoAdmin (admin.ModelAdmin):
    list_display = ['url', 'name', 'title']
    search_fields = ['url', 'name', "title"]

class PiadAdvertAdmin (admin.ModelAdmin):
    fields = ('advert_author', 'service', 'expiration_date', 'advert')
    readonly_fields = ['advert_author', 'advert', 'service']
    list_display = ['advert_id','advert_author', 'service']
    search_fields = ['advert__id', 'advert__author__username']
    list_filter = ['service',]
    
    def advert_id(self, obj):
        return obj.advert_id

    def advert_author(self, obj):
        return obj.advert.author

class CuttingWordsAdmin (admin.ModelAdmin):
    pass

class SublocalityDetectAdmin(admin.ModelAdmin):
    list_display = ('text','sublocality', 'city')
    search_fields = ["text"]
    list_filter = ['sublocality']

class PaidBannerAdmin(admin.ModelAdmin):
    list_display = ['city', 'place', 'start_date','expiration_date']


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['advert_id', 'pub_date', 'checked', 'reason', 'user', 'email', 'agent', 'phones_phones']
    search_fields = ['advert__id', 'phones__phone', 'reason']
    list_filter = ['phones__agent', 'checked']
    readonly_fields = ['pub_date', 'advert', 'phones', 'user', 'email']

    def advert_id(self, obj):
        return obj.advert_id

    def agent(self, obj):
        agents = obj.phones.all().values_list('agent', flat=True)
        agents = '-'.join([str(x) for x in agents])
        return agents

    def phones_phones(self, obj):
        phones = obj.phones.all().values_list('phone', flat=True)
        return '\n'.join([str(x) for x in phones])


class MessageForUsersAdmin(admin.ModelAdmin):
    list_display = ['location', 'text']


class SpamWordAdmin(admin.ModelAdmin):
    list_display = ['word']

class MetroDetectAdmin(admin.ModelAdmin):
    list_display = ['metro']

class StatAdvertAdmin(admin.ModelAdmin):
    list_display = ('source','creation_date', 'city')

admin.site.register(Phone, PhoneAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Advert, AdvertAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(UserData, UserDataAdmin,)
admin.site.register(Category, CategoryAdmin,)
admin.site.register(City, CityAdmin,)
admin.site.register(Seo, SeoAdmin,)
admin.site.register(PaidAdvert, PiadAdvertAdmin,)
admin.site.register(PaidBanner, PaidBannerAdmin)
admin.site.register(CuttingWords, CuttingWordsAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(MessageForUsers, MessageForUsersAdmin)
admin.site.register(SpamWord, SpamWordAdmin)
admin.site.register(SublocalityDetect, SublocalityDetectAdmin)
admin.site.register(MetroDetect)
admin.site.register(MetroLine)
admin.site.register(BigSublocality)
admin.site.register(Sublocality)
admin.site.register(Metro)
admin.site.register(StatAdvert,StatAdvertAdmin)


# for name, var in board_models.__dict__.items():
#     if type(var) is ModelBase:
#         try:
#             admin.site.register(var)
#         except:
#             pass
