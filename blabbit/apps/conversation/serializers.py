"""
Provides a way of serializing and deserializing the conversation app model
instances into representations such as json.
"""

from rest_framework import serializers
from blabbit.apps.conversation.models import Room, RoomFlag
from blabbit.apps.conversation.fields import GeometryField, ImageField
from blabbit.utils import human_readable_size
from django.conf import settings

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer to be used for getting and updating rooms.
    """
    
    # url field should lookup by 'name' not the 'pk'
    url = serializers.HyperlinkedIdentityField(view_name='room-detail',
                                               lookup_field='name')
    
    is_owner = serializers.SerializerMethodField('get_is_owner')
    
    # an untyped Field class, in contrast to the other typed fields such as
    # CharField, is always read-only. 
    # it will be used for serialized representations, but will not be used for
    # updating model instances when they are deserialized
    photo_thumbnail = serializers.Field(source='get_photo_thumbnail_url')   
    photo = ImageField(required=False)
    
    location = GeometryField(required=False)
    
    class Meta:
        model = Room
        fields = ('url', 'id', 'name', 'subject', 'is_owner', 
                  'photo_thumbnail', 'photo', 'location', 'likes_count', 
                  'created_at', 'last_modified')
        read_only_fields = ('id','name', 'likes_count', 'created_at', 
                            'last_modified')
        # lookup by 'name' not the 'pk'
        lookup_field = 'name'
        
    def validate_photo(self, attrs, source):
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
    
    def get_is_owner(self, obj):
        """
        get if current requester is room owner
        """
        return self.context['request'].user == obj.owner
    

class RoomFlagSerializer(serializers.ModelSerializer):
    """
    Serializer to be used for flagging rooms.
    """
        
    class Meta:
        model = RoomFlag
        fields = ('flag',)

    
    
    
