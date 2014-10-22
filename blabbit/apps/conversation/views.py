from rest_framework import mixins, generics, permissions, parsers, status
from rest_framework.response import Response

from blabbit.apps.rest import generics as custom_generics

from blabbit.apps.conversation.models import Room, RoomFlag
from blabbit.apps.conversation.serializers import RoomSerializer, \
    RoomFlagSerializer
from blabbit.apps.conversation.permissions import IsOwnerOrReadOnly

from blabbit.apps.account.models import User
from blabbit.apps.account.serializers import UserPublicOnlySerializer
from blabbit.apps.account.permissions import IsDetailOwner

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your views here.

class RoomList(generics.ListAPIView):
    """
    list all rooms
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of room objects containing public
    room data only.
    
    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ---------- 
    `url`              | URL of room object                   | _string_
    `id`               | ID of room object                    | _integer_
    `name`             | (unique) name of room object         | _string_
    `subject`          | room's subject                       | _string_
    `is_owner`         | is current requester the room owner? | _boolean_
    `photo_thumbnail`  | URL of room's thumbnail-sized photo  | _string_
    `photo`            | URL of room's full-sized photo       | _string_
    `location`         | room's associated longitude/latitude | _GEO object_
    `likes_count`      | count of likes room has received     | _integer_
    `created_at`       | room's creation date/time            | _date/time_
    `last_modified`    | last modified date of room object    | _date/time_

    #
    _`location` GEO object_ is of the format:
    
        "location": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464]
        }
    
    Note that the coordinates are of format `<longitude>, <latitude>`
    
    ## Publishing
    You can't create using this endpoint. 
    
    All room creations are done by the ejabberd server.
        
    
    ## Deleting
    You can't delete using this endpoint.
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        """
        Don't return expired rooms
        """
        
        earliest_date = timezone.now() - timedelta(
            seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
        return Room.objects.all().filter(created_at__gte=earliest_date)    
    

class RoomDetail(custom_generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve or update a room instance
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a room object containing the public room data.
    
    Name               | Description                          | Type
    ------------------ | ------------------------------------ | ---------- 
    `url`              | URL of room object                   | _string_
    `id`               | ID of room object                    | _integer_
    `name`             | (unique) name of room object         | _string_
    `subject`          | room's subject                       | _string_
    `is_owner`         | is current requester the room owner? | _boolean_
    `photo_thumbnail`  | URL of room's thumbnail-sized photo  | _string_
    `photo`            | URL of room's full-sized photo       | _string_
    `location`         | room's associated longitude/latitude | _GEO object_
    `likes_count`      | count of likes room has received     | _integer_
    `created_at`       | room's creation date/time            | _date/time_
    `last_modified`    | last modified date of room object    | _date/time_
    
    #
    _`location` GEO object_ is of the format:
    
        "location": {
            "type": "Point",
            "coordinates": [-123.0208, 44.0464]
        }
    
    Note that the coordinates are of format `<longitude>, <latitude>`
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    Ideally we would prevent deletions using this endpoint and leave all
    deletions to the ejabberd server.
    
    ### Permissions
    * Only authenticated users can delete rooms they own
    
    ### Response
    If deletion is successful, HTTP 204: No Content, otherwise an error message
    
    
    ## Updating
    Submitting a photo requires capturing a photo via file upload as 
    **multipart/form-data** then using the `photo` parameter. 
    
    Note that the request method must still be a PUT/PATCH
    
    ### Permissions
    * Only authenticated users can write to this endpoint.
    * Authenticated users can only update rooms they own.
    
    ### Fields
    Parameter    | Description                    | Type
    ------------ | ------------------------------ | ---------- 
    `subject`    | new subject for the  room      | _string_
    `location`   | new location for the room      | _string_
    `photo`     | new photo for the room. This will be scaled to generate `photo_thumbnail` | _string_
    
    ### Response
    If update is successful, a room object containing public data,
    otherwise an error message.
    
    
    ## Endpoints
    Name                    | Description                       
    ----------------------- | ----------------------------------------
    `members/<username>/`   | Add/remove authenticated user as a room member
    `likes/<username>/`     | Add/remove authenticated user as a room liker
    `flag/`                 | Flag a room for moderator review
    
    ##
    """
    
    parser_classes = (parsers.JSONParser, parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    # lookup by 'name' not the 'pk' but allow for case-insensitive lookups
    lookup_field = 'name__iexact'
    lookup_url_kwarg = 'name'
    
    def post_save(self, obj, created=False):
        """
        Handle information that is implicit in the incoming update request.
        If this is an authenticated user, then update room's owner to be the
        request's user.
        """
        if (self.request.user.is_authenticated()) and (obj.owner is None):
            obj.owner = self.request.user
            obj.members.add(self.request.user)
            obj.save()
    
    
class RoomMemberDetail(generics.GenericAPIView):
    """
    Get if a user is a member of a room, and add or remove them from room.
    
    ## Reading
    ### Permissions
    * Only authenticated users viewing their own user's membership in a room
      can read this endpoint.
    
    ### Fields
    If user is a member, **_true_** else **__false__**. Will get an error
    message if room/user don't exist or not authorized for this action.
    
    
    ## Publishing
    ### Permissions
    * Only authenticated users can add themselves as members of a room.
    
    ### Fields
    None
    
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Deleting
    ### Permissions
    * Only authenticated users can remove themselves as members of a room.
    
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated, IsDetailOwner)
    serializer_class = UserPublicOnlySerializer
    # IsDetailOwner permission expects to use the lookup field to get the object
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'
        
    def get(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        # IsDetailOwner checks for existence of the user.
        
        is_room_member = False
        try:
            user = room.members.get(username__iexact=username)
            is_room_member = True
        except User.DoesNotExist:
            pass

        return Response({
                'detail':is_room_member
                })
    
    def post(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        user = get_object_or_404(User, username__iexact=username)
        room.members.add(user)
        return Response({
                'detail':True
                })
    
    def delete(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        user = get_object_or_404(User, username__iexact=username)
        room.members.remove(user)
        return Response({
                'detail':True
                })
    
    
class RoomLikeDetail(generics.GenericAPIView):
    """
    Get if a user likes a room, like or unlike a room
    
    ## Reading
    ### Permissions
    * Only authenticated users viewing their own user's room like can read this
      endpoint.
    
    ### Fields
     If user likes room, **_true_** else **__false__**. Will get an error
    message if room/user don't exist or not authorized for this action.
    
    
    ## Publishing
    ### Permissions
    * Only authenticated users can like a room.
    
    ### Fields
    None
    
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Deleting
    ### Permissions
    * Only authenticated users can unlike a room.
    
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Updating
    You can't update using this endpoint
   
    """
    
    permission_classes = (permissions.IsAuthenticated, IsDetailOwner)
    serializer_class = UserPublicOnlySerializer
    # IsDetailOwner permission expects to use the lookup field to get the object
    lookup_field = 'username__iexact'
    lookup_url_kwarg = 'username'
        
    def get(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        # IsDetailOwner checks for existence of the user.
        likes_room = False
        try:
            user = room.likes.get(username__iexact=username)
            likes_room = True
        except User.DoesNotExist:
            pass

        return Response({
                'detail':likes_room
                })
    
    def post(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        user = get_object_or_404(User, username__iexact=username)
        room.likes.add(user)
        room.save() # force an update of likes_count room attribute
        return Response({
                'detail':True
                })
    
    def delete(self, request, name, username, format=None):
        room = get_object_or_404(Room, name__iexact=name)
        user = get_object_or_404(User, username__iexact=username)
        room.likes.remove(user)
        room.save() # force an update of likes_count room attribute
        return Response({
                'detail':True
                })
    


class RoomFlagDetail(generics.GenericAPIView):
    """
    Flag a room for moderator review and
        
    ## Reading
    You can't read using this endpoint.
        
    
    ## Publishing
    ### Permissions
    * Anyone can create using this endpoint. Authenticated users will be tied to
      the flag request to ensure we don't log duplicate flag requests from them.
    
    ### Fields
    None
    
    ### Response
    If successful, **_true_**, else an error message.
    
    
    ## Deleting
    You can't delete using this endpooint.
    
    
    ## Updating
    You can't update using this endpoint.
   
    """
    
    permission_classes = (permissions.AllowAny,)
    queryset = Room.objects.all()
    serializer_class = RoomFlagSerializer
    
    # lookup by 'name' not the 'pk' but allow for case-insensitive lookups
    lookup_field = 'name__iexact'
    lookup_url_kwarg = 'name'
        
    def post(self, request, name, format=None):
        room = self.get_object()
        user = None
        if request.user.is_authenticated():
            user = request.user
        
        RoomFlag.objects.get_or_create(
            user=user, 
            room=room)
        
        return Response({
                'detail':True
                })
    

    
