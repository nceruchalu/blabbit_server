from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from blabbit.apps.account import views

# URL structure inspired by github API: https://developer.github.com/v3/users/

urlpatterns = patterns('',
                       # user list
                       url(r'^users/$', views.UserList.as_view(), 
                           name='user-list'),                   
                       
                       # user details and list of a single user
                       url(r'^users/(?P<username>[\w.+-]+)/$',
                           views.UserDetail.as_view(), name='user-detail'),
                       url(r'^users/(?P<username>[\w.+-]+)/rooms/$',
                           views.UserRoomList.as_view(), name='user-room-list'),
                       url(r'^users/(?P<username>[\w.+-]+)/contacts/$',
                           views.UserContactList.as_view(), 
                           name='user-contact-list'),
                       
                       # authenticated user's details and associated lists
                       url(r'^user/$',
                           views.AuthenticatedUserDetail.as_view(), 
                           name='user-auth-detail'),
                       url(r'^user/rooms/$',
                           views.AuthenticatedUserRoomList.as_view(), 
                           name='user-auth-room-list'),
                       url(r'^user/contacts/$',
                           views.AuthenticatedUserContactList.as_view(), 
                           name='user-auth-contact-list'),

                       # obtain auth token given a username and password
                       url(r'^account/auth/token/$', 
                           views.ObtainExpiringAuthToken.as_view(),
                           name='obtain_auth_token'),
                       
                       # change password
                       url(r'^account/password/change/$',
                           views.PasswordChange.as_view(),
                           name='acct_password_change'),
                      
                       # request password reset
                       url(r'^account/password/reset/$',
                           views.PasswordReset.as_view(),
                           name='acct_password_reset'),
                       )

urlpatterns = format_suffix_patterns(urlpatterns)
