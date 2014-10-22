"""
URLs that aren't included in the REST API
"""

from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views
from blabbit.apps.account import views

# Using modified versions of django registration password reset templates.
# Find originals here: https://github.com/django/django/tree/master/django/contrib/admin/templates/registration

urlpatterns = patterns('',
                       # complete password reset
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           {'template_name':
                                'account/password_reset_confirm.html',
                            'post_reset_redirect':
                                'acct_password_reset_complete'},
                           name='acct_password_reset_confirm'),
                       
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           {'template_name':
                                'account/password_reset_complete.html'},
                           name='acct_password_reset_complete'),
                    
                       )

