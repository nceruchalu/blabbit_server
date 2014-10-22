from blabbit.apps.account.models import User, AuthToken
from blabbit.apps.account.serializers import UserSerializer, \
    UserPublicOnlySerializer, UserCreationSerializer, PasswordResetSerializer, \
    PasswordChangeSerializer, AuthTokenSerializer
from blabbit.apps.account.permissions import IsOwnerOrReadOnly, IsDetailOwner

from blabbit.apps.conversation.serializers import RoomSerializer
from blabbit.apps.conversation.models import Room
from blabbit.apps.relationship.utils import get_contacts

from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics, status, permissions, parsers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from blabbit.apps.rest import generics as custom_generics

# Create your views here.

class UserList(generics.CreateAPIView):
    """
    List all users or create a new user.
    
    ## Reading
    You can't read using this endpoint. While it would seem nice for this API
    endpoint to list all users you can imagine why this is a user privacy issue.
        
    ### Fields
    If reading this endpoint returned a list of user objects, each user object
    would only contains public user data.
    
    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ---------- 
    `url`              | URL of user object                   | _string_
    `id`               | ID of user object                    | _integer_
    `username`         | username of user object              | _string_
    `first_name`       | first name of user object            | _string_
    `avatar_thumbnail` | URL of user's thumbnail-sized avatar | _string_
    `last_modified`    | last modified date of user object    | _date/time_
     
    
    ## Publishing
    ### Permissions
    * Anyone can create using this endpoint.
    
    ### Fields
    Parameter  | Description                                       | Type
    ---------- | ------------------------------------------------- | ---------- 
    `username` | username for the new user. This field is required | _string_
    `password` | password for the new user. This field is required | _string_
    `email`    | email for the new user. This field is optional    | _string_
    
    ### Response
    If create is successful, a limited scope user object, otherwise an error 
    message. 
    The limited scope user object has the following fields:
    
    Name       | Description                          | Type
    ---------- | ------------------------------------ | ---------- 
    `url`      | URL of new user object               | _string_
    `id`       | The ID of the newly created user     | _integer_
    `username` | username as provided during creation | _string_
    `email`    | email as provided during creation    | _string_
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    
    ## Endpoints
    Name                      | Description                       
    ------------------------- | ----------------------------------------
    `<username>/`             | Retrieve or update details of a user instance
    
    ##
    """
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """
        a POST request implies a user creation so return the serializer for
        user creation. 
        All other requests will be GET so use the privacy-respecting user 
        serializer
        """
        if self.request.method == "POST":
            return UserCreationSerializer
        else: 
            return UserPublicOnlySerializer


# -----------------------------------------------------------------------------
# USER'S DETAILS AND ASSOCIATED LISTS
# -----------------------------------------------------------------------------

class UserDetail(custom_generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a user instance
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    * Authenticated users reading their own user instance get additional private
      data.
    
    ### Fields
    Reading this endpoint returns a user object containing the public user data.
    An authenticated user reading their own user also gets to see the private
    user data.
    
    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ---------- 
    `url`              | URL of user object                   | _string_
    `id`               | ID of user                           | _integer_
    `username`         | username of user object              | _string_
    `first_name`       | first name of user object            | _string_
    `avatar_thumbnail` | URL of user's thumbnail-sized avatar | _string_
    `last_modified`    | last modified date of user object    | _date/time_
    `email`            | email of user object. **_private_**. | _string_
    `rooms_url` | URL of user's rooms sub-collection. **_private_**.  | _string_
    `contacts_url` | URL of user's contacts sub-collection. **_private_**. | _string_
    
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    Submitting an avatar requires capturing a photo via file upload as 
    **multipart/form-data** then using the `avatar` parameter. 
    
    Note that the request method must still be a PUT/PATCH
    
    ### Permissions
    * Only authenticated users can write to this endpoint.
    * Authenticated users can only update their own user instance.
    
    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ----------
    `first_name` | new first name for the  user   | _string_
    `email`      | new email for the user         | _string_
    `avatar`     | new avatar image for the user. This will be scaled to generate `avatar_thumbnail` | _string_
    
    ### Response
    If update is successful, a user object containing public and private data, 
    otherwise an error message.
        
    
    ## Endpoints
    Name                    | Description                       
    ----------------------- | ----------------------------------------
    [`rooms`](rooms/)       | All the rooms this user is a member of
    [`contacts`](contacts/)  | All this user's contacts i.e. friends and friend requests (from and to)

    ##
    """
    
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = User.objects.all()
    
    # lookup by 'username' not the 'pk' but allow for case-insensitive lookups
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'

    def get_serializer_class(self):
        """
        You only get to see private data if you request details of yourself.
        Otherwise you get to see a limited view of another user's details
        """
        # I purposely dont call self.get_object() here so as not to raise
        # permission exceptions.
        serializer_class = UserPublicOnlySerializer
        try:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            user_object = User.objects.get(**filter)
            if self.request.user == user_object:
                serializer_class = UserSerializer
        except User.DoesNotExist:
            pass # serializer_class already setup
        
        return serializer_class
            
    
    # unused function
    def blabbit_get_object(self):
        """
        try getting an object by username, and if that fails try getting an
        object by pk.
        """
        from django.shortcuts import get_object_or_404
        queryset = self.get_queryset()
        try:
            obj = User.objects.get(username__iexact=self.kwargs['username'])
        except User.DoesNotExist:
            obj = get_object_or_404(queryset, pk=self.kwargs['username'])
        
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
                

class UserRoomList(generics.ListAPIView):
    """
    List all rooms a user participates in.
    
    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `rooms` sub-collection can read
      this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of [Room objects](/api/v1/rooms/) 
    containing each room's public data only.
     
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated, IsDetailOwner,)
    serializer_class = RoomSerializer
    # IsDetailOwner permission expects to use the lookup field and url kwarg 
    # to get the object
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        """
        This view should return a list of all rooms for the user as determined
        by the lookup parameters of the view.
        Be sure to exclude expired rooms.
        """
        
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs.get(lookup_url_kwarg, None)
                        
        if lookup is not None:
            filter_kwargs = {self.lookup_field: lookup}
            user = get_object_or_404(User, **filter_kwargs)
            earliest_date = timezone.now() - timedelta(
                seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
            return user.rooms.all().filter(created_at__gte=earliest_date) 
        return Room.objects.none()
    
    def get_paginate_by(self):
        """
        Return all rooms the user is a member of.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count() 
        return count if (count > 0) else self.paginate_by


class UserContactList(generics.ListAPIView):
    """
    List all contacts of a user.
    
    ## Reading
    ### Permissions
    * Only authenticated users viewing their own `contacts` sub-collection can 
      read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of 
    [contact User objects](/api/v1/users/). 
    
    Each contact object only contains the contact's public data. You get the 
    user's  relationship with each contact from ejabberd.
     
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated, IsDetailOwner,)
    serializer_class = UserPublicOnlySerializer
    # IsDetailOwner permission expects to use the lookup field and url kwarg 
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        """
        This view should return a list of all contacts of the user as determined
        by the lookup parameters of the view.
        """
        
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup = self.kwargs.get(lookup_url_kwarg, None)
                        
        if lookup is not None:
            filter_kwargs = {self.lookup_field: lookup}
            user = get_object_or_404(User, **filter_kwargs)
            return get_contacts(user)
        
        return User.objects.none()
    
    def get_paginate_by(self):
        """
        Return all contacts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


# -----------------------------------------------------------------------------
# AUTHENTICATED USER'S DETAILS AND ASSOCIATED LISTS
# -----------------------------------------------------------------------------

class AuthenticatedUserDetail(custom_generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user
    
    ## Reading
    ### Permissions
    * Authenticated users
    
    ### Fields
    Reading this endpoint returns a user object containing the authenticated
    user's public and private data.
    
    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ---------- 
    `url`              | URL of user object                   | _string_
    `id`               | ID of user                           | _integer_
    `username`         | username of user object              | _string_
    `first_name`       | first name of user object            | _string_
    `avatar_thumbnail` | URL of user's thumbnail-sized avatar | _string_
    `email`            | email of user object. **_private_**. | _string_
    `rooms_url` | URL of user's rooms sub-collection. **_private_**.  | _string_
    `contacts_url` | URL of user's contacts sub-collection. **_private_**. | _string_
    
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    Submitting an avatar requires capturing a photo via file upload as 
    **multipart/form-data** then using the `avatar` parameter. 
    
    Note that the request method must still be a PUT/PATCH
    
    ### Permissions
    * Only authenticated users can write to this endpoint.
    
    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ----------
    `first_name` | new first name for the  user   | _string_
    `email`      | new email for the user         | _string_
    `avatar`     | new avatar image for the user. This will be scaled to generate `avatar_thumbnail` | _string_
    
    ### Response
    If update is successful, a user object containing public and private data, 
    otherwise an error message.
        
    
    ## Endpoints
    Name                    | Description                       
    ----------------------- | ----------------------------------------
    [`rooms`](rooms/)       | All the rooms authenticated user is a member of
    [`contacts`](contacts/)  | All authenticated user's contacts i.e. friends and friend requests (from and to)

    ##
    """
    
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
            
    def get_object(self):
        """
        Simply return authenticated user.
        No need to check object level permissions
        """
        return self.request.user


class AuthenticatedUserRoomList(generics.ListAPIView):
    """
    List all rooms authenticated user participates in.
    
    ## Reading
    ### Permissions
    * Only authenticated users can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of [Room objects](/api/v1/rooms/) 
    containing each room's public data only.
         
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RoomSerializer
            
    def get_queryset(self):
        """
        This view should return a list of all rooms for the request's user
        """
        user = self.request.user
        earliest_date = timezone.now() - timedelta(
            seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
        return user.rooms.all().filter(created_at__gte=earliest_date)
    
    def get_paginate_by(self):
        """
        Return all rooms the user is a member of.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count() 
        return count if (count > 0) else self.paginate_by
        

class AuthenticatedUserContactList(generics.ListAPIView):
    """
    List all contacts of authenticated user.
    
    ## Reading
    ### Permissions
    * Only authenticated users can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of 
    [contact User objects](/api/v1/users/). 
    
    Each contact object only contains the contact's public data. You get the 
    user's relationship with each contact from ejabberd.
     
    
    ## Publishing
    You can't create using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserPublicOnlySerializer
            
    def get_queryset(self):
        """
        This view should return a list of all contacts of the request's user
        """
        user = self.request.user
        return get_contacts(user)
    
    def get_paginate_by(self):
        """
        Return all contacts of the user.
        If there are no objects use the default paginate_by.
        """
        # we can't just use a count() query as get_queryset() actually
        # returns a list not a queryset
        count = len(self.get_queryset())
        return count if (count > 0) else self.paginate_by


# -----------------------------------------------------------------------------
# USER AUTHENTICATION CREDENTIALS
# -----------------------------------------------------------------------------

class ObtainExpiringAuthToken(ObtainAuthToken):
    """
    Subclass of rest_framework.authtoken.views.ObtainAuthToken that refreshes 
    and returns the authentication token each time it is requested.
    
    This class only accepts a **POST** with the following params:
    
    * `username`
    * `password`
    
    A valid username/password pair gets a response with:
    
    * `token`
    """
    serializer_class = AuthTokenSerializer
    permission_classes = (permissions.AllowAny,)
        
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        
        if serializer.is_valid():
            # get or create user's corresponding token
            token, created = \
                AuthToken.objects.get_or_create(user=serializer.object['user'])
            
            now = timezone.now()
            # a stale token is one that is older than SESSION_COOKIE_AGE
            stale_token = (now - token.created) > \
                timedelta(seconds=settings.SESSION_COOKIE_AGE)
            
            if not created and stale_token:
                # refresh the token if it isn't newly created and it's stale
                token.created = now
                
                # attempt creating a unique key. Don't want to keep looping
                # while making DB calls so will give this one-shot. If the
                # first key generated is unique then use it, else tough luck.
                new_key = token.generate_key()
                if not AuthToken.objects.filter(key=new_key).count():
                    token.key = new_key
                
                token.save()
            
            # finally return token to user
            return Response({'token': token.key})
        
        # getting here means there was an error with the request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChange(generics.GenericAPIView):
    """
    Provides password change functionality. Does this by calling 
    django.contrib.auth's PasswordChangeForm save method.
    
    Clients should change password by passing the following POST parameters:
    * `old_password`
    * `new_password1`
    * `new_password2`
    """
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordChangeSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            # Create PasswordChangeForm with the serializer
            password_change_form = PasswordChangeForm(user=self.request.user,
                                                      data=serializer.data)
            if password_change_form.is_valid():
                # TODO: reset token and force re-authentication
                password_change_form.save()
                
                # Return the success message with OK HTTP status
                return Response({
                        'detail':'You successfully changed your password'
                        })
            
            else:
                return Response(password_change_form.errors, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # coming this far means there likely was a problem
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# 3 views for password reset:
# - PasswordReset sends the mail
# - contrib.auth.views.password_reset_confirm checks the link the user has 
#   clicked and prompts for a new password
# - contrib.auth.views.password_reset_complete shows a success message for the 
#   above

class PasswordReset(generics.GenericAPIView):
    """
    Provides password reset functionality. Does this by calling 
    django.contrib.auth's PasswordResetForm save method
    
    Clients should reset password by passing the following POST parameters:
    
    * `email`
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (permissions.AllowAny,)
    
    subject_template_name = 'account/password_reset_email_subject.txt'
    email_template_name = 'account/password_reset_email.txt'
            
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            # Create PasswordResetForm with the serializer
            password_reset_form = PasswordResetForm(data=serializer.data)
            
            if password_reset_form.is_valid():
                # Set some values to be used for the send_email method.
                opts = {
                    'use_https': request.is_secure(),
                    'request': request,
                    'subject_template_name': self.subject_template_name,
                    'email_template_name': self.email_template_name,
                    }
                password_reset_form.save(**opts)
                
                # Return the success message with OK HTTP status
                return Response(serializer.data)
            
            else:
                return Response(password_reset_form.errors, 
                                status=status.HTTP_400_BAD_REQUEST)
        
        # coming this far means there likely was a problem
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

