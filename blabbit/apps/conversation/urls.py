from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from blabbit.apps.conversation import views

urlpatterns = patterns('',
                       # all rooms
                       url(r'^rooms/$', 
                           views.RoomList.as_view(), name='room-list'),
                       
                       # room details
                       url(r'^rooms/(?P<name>[\w.+-]+)/$', 
                           views.RoomDetail.as_view(), name='room-detail'),
                       
                       # room membership management
                       url(r'^rooms/(?P<name>[\w.+-]+)/members/(?P<username>[\w.+-]+)/$', 
                           views.RoomMemberDetail.as_view(), 
                           name='room-member-detail'),
                       
                       # room likes management
                       url(r'^rooms/(?P<name>[\w.+-]+)/likes/(?P<username>[\w.+-]+)/$', 
                           views.RoomLikeDetail.as_view(), 
                           name='room-like-detail'),
                       
                       # room flagging: for moderator review
                       url(r'^rooms/(?P<name>[\w.+-]+)/flag/$', 
                           views.RoomFlagDetail.as_view(), 
                           name='room-flag-detail'),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
