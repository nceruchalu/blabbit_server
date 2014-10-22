from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from blabbit.apps.explore import views

urlpatterns = patterns('',
                       
                       url(r'^explore/$', views.explore_root, 
                           name='explore_root'),
                       
                       url(r'^explore/popular/$',
                           views.PopularRoomsList.as_view(), 
                           name='explore-popular-list'),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
