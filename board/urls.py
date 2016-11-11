# -*- coding: utf-8 -*-
from board.models import City
from board.views import advert_create, advert_update, AdvertDelete,\
    AdvertDetail, AdvertList, redirect_url, other
from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from board.utils import ab_required

# this script for regexp into url<city>
city = []
for cc in City.objects.all():
    city.append(cc.slug)
list_of_the_cities = '|'.join(city)

#help_city_patterns = patterns('',
    #url(r'^basic/$', 'apps.help.views.views.basic'),
    #url(r'^advanced/$', 'apps.help.views.views.advanced'),
    #url(r'(?P<city>(('
    #    +list_of_the_city+
    #    r')))$',
    #    AdvertList.as_view(), name='advert-city'),
#)

urlpatterns = patterns('',
    # url(r'^forum/', include('pybb.urls', namespace='pybb')),
    url(r'^board/grid/save_chast.rar','board.views.save_txt', name='save_txt'),
    url(r'^(?P<city>(.*))/(?P<category>(.*))/save_chast.rar', 'board.views.save_city_txt', name='save_city_txt'),
    url(r'^board/grid/save_xls.xls','board.views.save_xls', name='save_xls'),
    url(r'^(?P<city>(.*))/(?P<category>(.*))/save_xls.xls', 'board.views.save_city_xls', name='save_city_xls'),
    url(r'^board/poll/$', 'board.views.poll', name='poll'),
    url(r'^board/add_to_agent/$', 'board.views.add_to_agent'),
    url(r'^board/add_to_owner/$', 'board.views.add_to_owner'),
    url(r'^board/add_to_unknown/$', 'board.views.add_to_unknown'),
    url(r'^board/del_all_advert/$', 'board.views.del_all_advert'),
    url(r'^board/add_to_spam/$', 'board.views.add_to_spam'),
    url(r'^board/add/$', advert_create, name='property_add'),
    url(r'^board/(?P<send_param>add)/(?P<token>\w+)$', 'personal.views.profile_mail', name='add_mail'),
    url(r'^board/(?P<pk>\d+)/up/$', 'board.views.advert_up', name='advert_up'),
    url(r'^board/(?P<pk>\d+)/update/$', advert_update, name='property_update'),
    url(r'^board/(?P<pk>\d+)/deactivate/$', 'board.views.advert_deactivate', name='advert_deactivate'),
    url(r'^board/(?P<pk>\d+)/delete/$', 'board.views.advert_to_delete', name='property_delete'),
    url(r'^board/recover_adv', 'board.views.advert_recover'),
    url(r'^yrl/$', 'board.views.yrl', name='yrl'),
    url(r'^board/get_extra_form/$', 'board.views.get_extra_form', name='get_extra_form'),
    url(r'^board/get_sublocality/$', 'board.views.get_sublocality', name='get_sublocality'),
    url(r'^board/image/remove/$', 'board.views.image_remove', name='image_remove'),
    url(r'^proverka_na_posrednika/$', 'board.views.check_phone', name='check_phone'),
    url(r'^advert_by_phone/$',  AdvertList.as_view()),
    url(r'^adverts_with_same_phones/(?P<pk>\d+)/$',  AdvertList.as_view(template_name='board/search.html')),
    url(r'^board/search$', AdvertList.as_view(template_name='board/search.html')),
    url(r'^board/add_to_fav/', 'board.views.add_to_fav'),
    url(r'^board/remove_from_fav/', 'board.views.remove_from_fav'),
    url(r'^board/add_pro_comment/', 'board.views.add_pro_comment'),
    url(r'^board/remove_pro_comment/', 'board.views.remove_pro_comment'),
    url(r'^board/add_pro_color_mark/', 'board.views.add_pro_color_mark'),
    url(r'^board/remove_pro_color_mark/', 'board.views.remove_pro_color_mark'),

    url(r'^board/apifiles/out/ki/key=77PL50', 'board.views.feed_kiev'),
    url(r'^board/apifiles/out/kh/key=6P7L50','board.views.feed_kharkov'),

    url(r'^board/advert_stats/(?P<city>(.*))/(?P<data>(.*))$', 'board.views.stats_parser', name="stats_parser"),
    url(r'^board/advert_stats/', AdvertList.as_view(template_name='board/advert_stats.html')),

    url(r'^board/grid/$', ab_required(
        AdvertList.as_view(template_name='board/pro_list.html')), name='start_grid'), 
    url(r'^board/grid/data$', 'board.views.grid_handler', name='grid_handler'),
    url(r'^board/grid/cfg/$', 'board.views.grid_config', name='grid_config'),
    # url(r'^board/(?P<send_param>grid)/(?P<token>\w+)$', 'personal.views.profile_mail', name='grid_mail'),
    url(r'^board/files/(?P<city>(.*))$', 'board.views.filetree', name="list"),
    url(r'^board/get-complaint$', 'board.views.get_complaint'),
    url(r'^board/set_city/$', 'board.views.set_city', name='set_city'),
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>(.*))/paid_adverts/$', AdvertList.as_view(), name='all_top'),
    url(r'^paid_adverts/$', AdvertList.as_view(), name='all_top'),
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>(.*))/similar/$', AdvertList.as_view(), name='similar_list'),
    
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>([\w-]+))/grid$', 
        ab_required(AdvertList.as_view(template_name='board/pro_list.html')), name='grid_ab'),
    # url to advert deteil
    url(r'^nedvizhimost/(?P<city>(.*))/(?P<category>(.*))/(?P<title>(.*))/(?P<pk>\d+)$', 
        redirect_url, name='redirect_url'),
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>(.*))/(?P<title>(.*))/(?P<pk>\d+)$', 
        AdvertDetail.as_view(), name='advert-detail'),
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>(.*))/(?P<title>(.*))/(?P<pk>\d+)/(?P<token>\w+)$', 
        AdvertDetail.as_view(), name='advert-token'),
    # url to category
    url(r'^nedvizhimost/(?P<city>(.*))/(?P<category>(.*))$', redirect_url, name='redirect_url'),
    #url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>(.*))/st-(?P<seo_url>(.*))$', AdvertList.as_view(), name='advert-category'),
    url(r'^(?P<city>(('+list_of_the_cities+')))/(?P<category>([\w-]+))$', 
        AdvertList.as_view(), name='advert-category'),
    # url to city
    url(r'^nedvizhimost/(?P<city>(.*))$', redirect_url, name='redirect_url'),
    url(r'^(?P<city>(('+list_of_the_cities+')))$', AdvertList.as_view(), name='advert-city'),
    #url(r'', include(help_city_patterns)),

    # url to other
    url(r'^(?P<other>(.*))$', TemplateView.as_view(template_name="index.html"), name='advert-other'),
    # url(r'^(?P<other>(.*))$', other, name='advert-other'),

)
