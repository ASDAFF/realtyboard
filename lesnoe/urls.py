from django.conf.urls import url, patterns
from django.views.generic import TemplateView
from lesnoe.views import GalleryView, ProjectList, ProjectDetail, FirstPage, Infrastr

urlpatterns = patterns('',
    url(r'^$', FirstPage.as_view(template_name='lesnoe/main.html'), name='lesnoe'),
    url(r'^/plan$', TemplateView.as_view(template_name='lesnoe/plan.html'), 
        name='lesnoe_plan'),
    url(r'^/infrastruktura$', Infrastr.as_view(
        template_name='lesnoe/infrastruktura.html'), name='lesnoe_infrastruktura'),
    url(r'^/gallery$', GalleryView.as_view(), name='lesnoe_gallery'),
    url(r'^/projects$', ProjectList.as_view(), name='lesnoe_projects'),
    url(r'^/project/(?P<pk>\d+)$', ProjectDetail.as_view(), name='lesnoe_project'),
    url(r'^/contacts$', TemplateView.as_view(template_name='lesnoe/contacts.html'), 
       name='lesnoe_contacts'),
    url(r'^/location$', TemplateView.as_view(template_name='lesnoe/location.html'), 
        name='lesnoe_location'),
)