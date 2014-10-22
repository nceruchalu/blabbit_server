"""
Object level permissions
"""

from rest_framework import permissions
from blabbit.apps.account.models import User

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow objects be visible to anyone, but only allow 
    actual user to edit (i.e. update/delete) it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request, so we'll always allow
        # GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the room.
        return obj == request.user


class IsDetailOwner(permissions.BasePermission):
    """
    Custom permission to allow views only to be visible to the actual user
    who owns the data at that detail view.
    
    Expects to be used on a detail view or a view with a lookup_field
    """
    
    def has_permission(self, request, view):
        user_owns_detail_view = False
        
        try:
            lookup_url_kwarg = view.lookup_url_kwarg or view.lookup_field
            lookup = view.kwargs.get(lookup_url_kwarg, None)
            
            if lookup is not None:
                filter_kwargs = {view.lookup_field: lookup}
                user_object = User.objects.get(**filter_kwargs)
                
                if request.user == user_object:
                    user_owns_detail_view = True
        
        except User.DoesNotExist:
            pass # user_owns_detail_view already set
        
        # permissions are only allowed to owner of the detail.
        return user_owns_detail_view
