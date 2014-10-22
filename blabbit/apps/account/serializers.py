"""
Provides a way of serializing and deserializing the account app model
instances into representations such as json.
"""

from rest_framework import serializers
from blabbit.apps.account.models import User
from blabbit.apps.relationship.utils import get_contacts
from blabbit.utils import human_readable_size

from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer to be used for getting and updating users.
    
    Most fields are read-only. Only writeable fields are: 
    - 'first_name'
    - 'email'
    """
    # url field should lookup by 'username' not the 'pk'
    url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='username')
    
    # an untyped Field class, in contrast to the other typed fields such as
    # CharField, is always read-only. 
    # it will be used for serialized representations, but will not be used for
    # updating model instances when they are deserialized
    avatar_thumbnail = serializers.Field(source='get_avatar_thumbnail_url')
    
    # uncomment this to specify if this user is in requester's contact list
    # is_contact = serializers.SerializerMethodField('get_is_contact')
    
    # ----------------------
    # Private Fields
    # -----------------------

    # `rooms` is a reverse relationship on the User model, so it will not be
    # included by default when using the ModelSerializer class, so we need
    # to add an explicit field for it.
    
    # uncomment this declaration show a list of names of rooms owned by the user
    # rooms = serializers.RelatedField(many=True, read_only=True)
    
    # show a link to the collection of a user's rooms
    rooms_url = serializers.HyperlinkedIdentityField(view_name='user-room-list',
                                                     lookup_field='username')
    
    # add max length check to email checks but keep it optional
    email = serializers.EmailField(max_length=254, required=False)
    
    # show a link to the collection of a user's contacts
    contacts_url = serializers.HyperlinkedIdentityField(
        view_name='user-contact-list', lookup_field='username')
    
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'first_name', 'avatar_thumbnail',
                  'avatar', 'last_modified', 
                  'email', 'rooms_url', 'contacts_url')
        read_only_fields = ('id','username', 'last_modified')
        write_only_fields = ('avatar',)
        # lookup by 'username' not the 'pk'
        lookup_field = 'username'
        
    def validate_avatar(self, attrs, source):
        """
        Check that the uploaded file size is within allowed limits
        """
        imgfile = attrs.get(source, False)
        if imgfile and imgfile.size > settings.MAX_IMAGE_SIZE:
            raise serializers.ValidationError(
                "Ensure this file's size is at most %s (it is %s)."
                % (human_readable_size(settings.MAX_IMAGE_SIZE), 
                   human_readable_size(imgfile.size)))
        
        return attrs
    
    def get_is_contact(self, obj):
        """
        Determine if user object is in requester's contact list or is requester.
        """
        user = self.context['request'].user
        if user.is_authenticated():
            if obj == user:
                return True
            contacts = get_contacts(user)
            if obj in contacts:
                return True
        return False


class UserPublicOnlySerializer(UserSerializer):
    """
    Serializer class to show a privacy-respecting version of users, i.e. public
    data only and so doesn't disclose personal information like 'email', 
    'rooms', 'contacts'
    
    All fields are read-only
    """
    
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'first_name', 'avatar_thumbnail', 
                  'last_modified',)
        read_only_fields = ('id', 'username', 'first_name', 'last_modified')


class UserCreationSerializer(UserSerializer):
    """
    Serializer to be used for creating users.
    """
    
    # username is a RegexField so that we can regulate on accepted characters
    username = serializers.RegexField(
        max_length=30,
        regex=r'^[\w.+-]+$',
        error_messages={'invalid': 
                        "Username may contain only letters, numbers and"
                        " ./+/-/_ characters."})
    
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'email')
        read_only_fields = ('id',)
        write_only_fields = ('password',) # Note: Password field is write-only
        
    def restore_object(self, attrs, instance=None):
        """
        Instantiate a new User instance.
        """
        assert instance is None, \
            'Cannot update users with UserCreationSerializer'
        user = User(email=attrs.get('email',''), username=attrs.get('username'))
        user.set_password(attrs.get('password'))
        return user
    
    def validate_username(self, attrs, source):
        """
        django usernames are case sensitive, so fix that here
        """
        # first make username lowercase for saving, as XMPP expects this
        attrs[source] = attrs[source].lower()
        value = attrs[source]
        
        try:
            user = User.objects.get(username__iexact=value)
            if user:
                raise serializers.ValidationError("User with this Username already exists.")
        except User.DoesNotExist:
            pass
        return attrs

class PasswordResetSerializer(UserSerializer):
    """
    Serializer for requesting a password reset by providing an e-mail.
    """
    
    class Meta:
        model = User
        fields = ('email',)


class PasswordChangeSerializer(UserSerializer):
    """
    Serializer for requesting a password change by providing
    """
    old_password = serializers.CharField(label="Old password")
    new_password1 = serializers.CharField(label="New password")
    new_password2 = serializers.CharField(label="New password confirmation")
    
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
        

class AuthTokenSerializer(serializers.Serializer):
    """
    customized AuthTokenSerializer
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # use lowercase username to enforce case-insensitivity and 
            # compatibility with XMPP
            username = username.lower()
            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)
                attrs['user'] = user
                return attrs
            else:
                msg = _('Unable to login with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "username" and "password"')
            raise serializers.ValidationError(msg)

