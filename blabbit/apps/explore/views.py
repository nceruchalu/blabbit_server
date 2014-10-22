from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from blabbit.apps.conversation.models import Room
from blabbit.apps.conversation.serializers import RoomSerializer

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your views here.

@api_view(('GET',))
def explore_root(request, format=None):
    return Response({
            'popular rooms': reverse('explore-popular-list', 
                                     request=request, format=format),
            })


class PopularRoomsList(generics.ListAPIView):
    """
    List of popular rooms.
        
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of [Room objects](/api/v1/rooms/) 
    containing each room's public data only.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = RoomSerializer
    
    def get_queryset(self):
        """
        This view should return the list of all rooms sorted by descending likes
        while excluding expired rooms
        """
        earliest_date = timezone.now() - timedelta(
            seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
        return Room.objects.all().filter(created_at__gte=earliest_date)\
            .order_by('-likes_count')
        

