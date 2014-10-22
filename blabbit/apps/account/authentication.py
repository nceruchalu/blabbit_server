from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from blabbit.apps.account.models import AuthToken

from django.utils import timezone
from django.conf import settings
from datetime import timedelta

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    A version of token based authentication where tokens expire.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ". For example:
    
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    model = AuthToken
    
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')
        
        # expire tokens that are too old
        earliest_valid_time = timezone.now() - \
            timedelta(seconds=settings.SESSION_COOKIE_AGE)
        if token.created < earliest_valid_time:
            raise exceptions.AuthenticationFailed('Token has expired')
        
        return (token.user, token)
