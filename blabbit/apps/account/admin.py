from django.contrib import admin
from blabbit.apps.account.models import User, AuthToken
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _

# Register your models here.

def delete_selected_u(modeladmin, request, queryset):
    """
    A version of the "deleted selected objects" action which calls the model's 
    `delete()` method. This is needed because the default version uses 
    `QuerySet.delete()`, which doesn't call the model's `delete()` method.
    
    Arguments:   
      - modeladmin: The User ModelAdmin
      - request:    HttpRequest object representing current request
      - queryset:   QuerySet of set of User objects selected by admin
    
    Return:      
      None
    
    Author:      
      Nnoduka Eruchalu
    """
    for obj in queryset:
        obj.delete()
delete_selected_u.short_description = "Delete selected user(s)"


class MyUserChangeForm(UserChangeForm):
    """
    Blabbit's version of the user change form which update's the metadata 
    specifying associated model to the custom User model
            
    Author:      
      Nnoduka Eruchalu
    """
    
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    """
    Blabbit's version of the user creation form which update's the metadata
    specifying associated model to the customer User model.
    
    Also overrides clean_username which directly references the built-in User
    model
    """
    
    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )
    
    class Meta(UserCreationForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    """
    Blabbit's version of the ModelAdmin associated with the User model. It is 
    modified to work with the custom User model
    
    Functions:   
      - get_actions: disable some actions for this ModelAdmin
            
    Author:
      Nnoduka Eruchalu
    """
    # use the custom "delete selected objects" action
    actions = [delete_selected_u]
    list_display =  ('username', 'first_name', 'email', 'date_joined',
                     'is_staff',)
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'email', 'avatar',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 
                                           'last_modified')}),
        )
    
    readonly_fields = ('last_login', 'date_joined', 'last_modified')
        
    # changing the displayed fields via `fieldsets` requires updating the form
    form = MyUserChangeForm
    # customizing the User model requires changing the add form
    add_form = MyUserCreationForm
    
    def get_actions(self, request):
        """
        Permanently disable the default "deleted selected objects" action for 
        this ModelAdmin
          
        Arguments:   
          - request: HttpRequest object representing current request
        Return:
          Updated list of actions.
                    
        Author:   
          Nnoduka Eruchalu
        """
        actions = super(MyUserAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


def delete_selected_a(modeladmin, request, queryset):
    """
    A version of the "deleted selected objects" action which calls the model's 
    `delete()` method. This is needed because the default version uses 
    `QuerySet.delete()`, which doesn't call the model's `delete()` method.
    
    Arguments:   
      - modeladmin: The AuthToken ModelAdmin
      - request:    HttpRequest object representing current request
      - queryset:   QuerySet of set of Room objects selected by admin
    
    Return:      
      None
    """
    for obj in queryset:
        obj.delete()
delete_selected_a.short_description = "Delete selected auth token(s)"

class AuthTokenAdmin(admin.ModelAdmin):
    """
    Representation of the AuthToken model in the admin interface.
    """
    # use the custom "delete sected objects" action
    actions = [delete_selected_a]
    
    list_display = ('key', 'user', 'created')
    fields = ('user',)
    ordering = ('-created',)
    
    def has_add_permission(self, request): 
        """
        Don't want users adding Auth Tokens through admin 
          
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
        actions = super(AuthTokenAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# Register UserAdmin
admin.site.register(User, MyUserAdmin)
# Register AuthTokenAdmin
admin.site.register(AuthToken, AuthTokenAdmin)



