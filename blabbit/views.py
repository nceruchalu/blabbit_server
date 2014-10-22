from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
            'authenticated user': reverse('user-auth-detail', request=request, 
                                          format=format),
            'users': reverse('user-list', request=request, format=format),
            'rooms': reverse('room-list', request=request, format=format),
            'explore':reverse('explore_root', request=request, format=format),
            'search': reverse('search_root', request=request, format=format),
            })
