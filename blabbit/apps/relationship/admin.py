from django.contrib import admin
from blabbit.apps.relationship.models import Friendship

# Register your models here.

class FriendshipAdmin(admin.ModelAdmin):
    """
    Representation of the Friendship model in the admin interface.
    This model is read-only via admin interface
    """
    list_display = ('username_username', 'jid', 'subscription', 'ask')
    readonly_fields = ('username', 'jid', 'nick', 'subscription', 'ask', 
                       'askmessage', 'server', 'subscribe', 'type','created_at')
    search_fields = ('username__username', 'username__first_name')
        
    def has_add_permission(self, request): 
        """
        Don't want users adding Relationships through admin 
          
        Arguments:   
          - request: HttpRequest object representing current request
        Return:      
          (Boolean) False
        """
        return False
    
    def get_actions(self, request):
        """
        Permanently disable the default "deleted selected objects" action for 
        this ModelAdmin
          
        Arguments:   
          - request: HttpRequest object representing current request
        Return:      
          Updated list of actions.
                    
        Author:      Nnoduka Eruchalu
        """
        actions = super(FriendshipAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def username_username(self, instance):
        """
        return username of associate user
        """
        return instance.username.username

admin.site.register(Friendship, FriendshipAdmin)
