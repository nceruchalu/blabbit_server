from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet 

from blabbit.apps.account.models import User
from blabbit.apps.account.serializers import UserPublicOnlySerializer

from blabbit.apps.conversation.models import Room
from blabbit.apps.conversation.serializers import RoomSerializer

from blabbit.utils import list_dedup

from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your views here.

@api_view(('GET',))
def search_root(request, format=None):
    return Response({
            'search users': reverse('user-search-list', request=request, 
                                    format=format),
            'search rooms': reverse('room-search-list', request=request, 
                                    format=format),
        })

class SearchResultList(generics.ListAPIView):
    """
    List results of search given any queryset limited to a specific model.
    
    This class is required to be subclassed and provided with the following
    properties:
    * model
    * serializer_class
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of user objects and room objects,
    each only containing public user data.
         
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)
    
    
    def get_queryset(self):
        query = ''
        results = []
        
        if self.request.QUERY_PARAMS.get('q'):
            # limit searchqueryset to appropriate model
            searchqueryset = SearchQuerySet().models(self.model)
            # then perform a search on specific model.
            form = SearchForm(self.request.QUERY_PARAMS, 
                              searchqueryset=searchqueryset, load_all=True)
            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
                results = self.filter_results(results)
                # for odd reasons there are duplicates in the haystack results.
                results = list_dedup([r.object for r in results])
        
        return results
    
    def filter_results(self, results):
        """
        Filter the serch results appropriate. 
        This default implementation does nothing but return the argument.
        
        Arguments:
        - results: SearchQuerySet which contains the results of a search query
        """
        return results


class UserSearchResultList(SearchResultList):
    """
    List results of search on users
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of user objects containing only
    public data.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    
    model = User
    serializer_class = UserPublicOnlySerializer


class RoomSearchResultList(SearchResultList):
    """
    List results of search on rooms
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of room objects containing only
    public data.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    
    model = Room
    serializer_class = RoomSerializer
    
    def filter_results(self, results):
        """
        Filter search results to exclude expired rooms
        """
        earliest_date = timezone.now() - timedelta(
            seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
        return results.filter(created_at__gte=earliest_date)   

