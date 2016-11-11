# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from views import NewsList, NewsCreate, NewsDetail, NewsUpdate, NewsDelete

from board.utils import ed_required, ed_required_redactor
from news import views

ext_urls = patterns('',
    url(r'/create/$', ed_required_redactor(NewsCreate.as_view()), name='news-create'),
    url(r'^/delete/(?P<slug>(.*))$', ed_required(NewsDelete.as_view()), name='news-delete'),
    url(r'^/update/(?P<slug>(.*))$', ed_required_redactor(NewsUpdate.as_view()), name='news-update'),
    url(r'^/(?P<slug>(.*))$', NewsDetail.as_view(), name='news-detail'),
    url(r'$', NewsList.as_view(), name='news-list'),        
)

urlpatterns = patterns('',
    url(r'^contacts', TemplateView.as_view(template_name='news/contacts.html'), name='contacts'),
    url(r'^oplata$', views.Oplata.as_view(), name='oplata'),
    url(r'^(?P<send_param>oplata)/(?P<token>\w+)$', 'personal.views.profile_mail', name='oplata_mail'),
    url(r'^novosty', include(ext_urls)),
    url(r'^statiy/poleznoe', include(ext_urls)),
    url(r'^novovvedeniy_saita', include(ext_urls)),
    url(r'^zadavaemie_voprosy', include(ext_urls)),
    url(r'^rielter', views.TemplateView.as_view(template_name='news/rielter.html')),
    url(r'^black_list$', views.BlackListList.as_view(), name='black_list'),
    url(r'^black_list/(?P<city>)$', views.BlackListList.as_view(), name='black_list_city'),
    url(r'^black_list/new_post$', login_required(views.BlackListCreate.as_view()), 
        name='new_black_post'),
    url(r'^black_list/add_black_comment$', login_required(views.add_black_comment),
        name='add_black_comment'),
    url(r'^black_list/del_black_comment$', login_required(views.del_black_comment),
        name='del_black_comment'),
    url(r'^black_list/(?P<pk>(\d+))$', views.BlackListDetail.as_view(),
        name='black_list_detail'),

    



    # url(r'/detail/(?P<article_id>(.*))$', views.news_detail, name='detail_news'),
    # url(r'/edit/(?P<article_id>(.*))$', views.news_edit, name='news_edit'),
    # url(r'', views.news_list, name='news_list'),
)
