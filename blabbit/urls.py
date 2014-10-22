from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

from django.contrib.gis import admin
admin.autodiscover()

# REST API URLS
api_urlpatterns = patterns('',
                           url(r'^$', 'blabbit.views.api_root',
                               name='api_root'),
                           url(r'', include('blabbit.apps.account.urls')),
                           url(r'', include('blabbit.apps.conversation.urls')),
                           url(r'', include('blabbit.apps.explore.urls')),
                           url(r'', include('blabbit.apps.search.urls')),
                           url(r'', include('blabbit.apps.feedback.urls')),
                           # login and logout views for the browseable API
                           url(r'^browse/',include('rest_framework.urls', 
                                                   namespace='rest_framework')),
                           )

urlpatterns = patterns('',
                       
                       # REST API URLS with version number
                       url(r'^api/v1/', include(api_urlpatterns)),
                       
                       # Regular web URLs
                       url(r'^$', 
                           TemplateView.as_view(template_name="home.html"), 
                           name='home'),
                       
                       url(r'^privacy/$', 
                           TemplateView.as_view(template_name="privacy.html"), 
                           name='privacy'),
                       
                       url(r'^terms/$', 
                           TemplateView.as_view(template_name="terms.html"), 
                           name='terms'),
                       
                       url(r'', include('blabbit.apps.account.web_urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       
)
