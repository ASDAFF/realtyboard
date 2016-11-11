from django.conf.urls import patterns, url

from tour import views

urlpatterns = patterns('',
    # ex: /tour/
    url(r'^$', 'tour.views.example', name='index'),
)