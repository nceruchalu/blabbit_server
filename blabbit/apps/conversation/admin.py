from django.contrib.gis import admin
from blabbit.apps.conversation.models import Room, RoomFlag

# Register your models here.

def delete_selected_r(modeladmin, request, queryset):
    """
    A version of the "deleted selected objects" action which calls the model's 
    `delete()` method. This is needed because the default version uses 
    `QuerySet.delete()`, which doesn't call the model's `delete()` method.
    
    Arguments:   
      - modeladmin: The Room ModelAdmin
      - request:    HttpRequest object representing current request
      - queryset:   QuerySet of set of Room objects selected by admin
    
    Return:      
      None
    """
    for obj in queryset:
        obj.delete()
delete_selected_r.short_description = "Delete selected room(s)"


class RoomAdmin(admin.OSMGeoAdmin):
    """
    Representation of the Room model in the admin interface.
    The ejabberd specific fields of this are read-only via the admin interface.
    
    We want GeoDjango to use an Open Street Map layer in the admin hence a
    subclass
    """
    # use the custom "delete sected objects" action
    actions = [delete_selected_r]
    
    list_display = ('name', 'subject', 'owner', 'created_at')
    fields = ('name', 'subject', 'photo', 'owner', 'members', 'likes', 
              'likes_count',
              'location', 'host', 'created_at', 'last_modified', 'opts')
    #filter_horizontal = ('members',)
    readonly_fields = ('name', 'members', 'likes','host', 'opts', 'created_at', 
                       'last_modified')
    search_fields = ('name', 'owner__username', 'owner__first_name')
            
    def has_add_permission(self, request): 
        """
        Don't want users adding Rooms through admin 
          
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
        """
        actions = super(RoomAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class RoomFlagAdmin(admin.ModelAdmin):
    """
    Representation of the Room Flag model in the admin interface.
    """
    list_display = ('user', 'room', 'flag', 'flag_date')
    fields = ('user', 'room', 'flag', 'flag_date')
    readonly_fields = ('flag_date',)
    search_fields = ('room__subject', 'user__username', 'user__first_name')
            
    
admin.site.register(Room, RoomAdmin)
admin.site.register(RoomFlag, RoomFlagAdmin)
