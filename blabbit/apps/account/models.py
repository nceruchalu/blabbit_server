from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse

from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, Adjust
from blabbit.utils import get_upload_path

import binascii
import os

# Create your models here.

# HELPER FUNCTIONS
def get_avatar_path(instance, filename):
    return get_upload_path(instance, filename, 'img/u/')


class User(AbstractUser):
    """
    Extended User class
    
    There are two approaches to extending Django's User class:
    - A related model that had a 1:1 rlp with django.contrib.auth.models.User
      + This has the caveat of extra joins to get user profile
    - Subclass django.contrib.auth.models.AbstractUser
      + This is more efficient, but less modular
      
    I choose to go for option 2 because I want speed
            
    Author:     
      Nnoduka Eruchalu
    """
    
    # last modified date to be used by client apps for sync purposes.
    # ref: http://stackoverflow.com/a/5052208
    last_modified = models.DateTimeField(auto_now=True)
    
    # avatar
    avatar = models.ImageField(upload_to=get_avatar_path, blank=True)
    
    # imagekit spec for avatar shown in mobile app's UITableViews
    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[SmartResize(width=120, height=120),
                    Adjust(contrast = 1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality':90})
    
    # this is used for tracking avatar changes
    # ref: http://stackoverflow.com/a/1793323
    __original_avatar = None
    
    def get_avatar_thumbnail_url(self):
        """
        get url of avatar's thumbnail. If there isn't an avatar_thumbnail then
        return an empty string
        """
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ''
        
    def get_full_name(self):
        """
        Get user's full name
        If there is a valid full name then use that, otherwise use the username
        [prepended with an '@']
    
        Arguments:   
          None
        Return:      
          (str) user's full name
          
        Author: 
          Nnoduka Eruchalu
        """
        return (super(User, self).get_full_name() or ('@'+self.username))
    
    
    def __unicode__(self):
        """
        Override the representation of users to use full names.
        
        Arguments:   
          None
        Return:      
          (str) user's full name
          
        Author:     
          Nnoduka Eruchalu
        """
        return self.get_full_name()
        
    
    def delete_avatar_files(self, instance):
        """
        Delete a user's avatar files in storage
        - First delete the user's ImageCacheFiles on storage. The reason this 
          must happen first is that deleting source file deletes the associated 
          ImageCacheFile references but not the actual ImageCacheFiles in 
          storage.
        - Next delete source file (this also performs a delete on the storage 
          backend)
                
        Arguments:   
          - instance: User object instance to have files deleted
        Return:      
          None 
          
        Author:      
          Nnoduka Eruchalu
        """
        # get avatar_thumbnail location and delete it
        instance.avatar_thumbnail.storage.delete(instance.avatar_thumbnail.name)
        # delete avatar
        instance.avatar.delete()
    
    
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.__original_avatar = self.avatar
                
    
    def save(self, *args, **kwargs):
        """
        On instance save ensure old image files are deleted if images are 
        updated.
                            
        Arguments:   
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None 
          
        Author:
          Nnoduka Eruchalu
        """
        if self.__original_avatar and self.avatar != self.__original_avatar:
            # avatar has changed and this isn't the first avatar upload, so
            # delete old files.
            orig = User.objects.get(pk=self.pk)
            self.delete_avatar_files(orig)
                    
        super(User, self).save(*args, **kwargs)
        # update the image file tracking properties
        self.__original_avatar = self.avatar
                
    
    def delete(self, *args, **kwargs):
        """
        Default model delete doesn't delete files on storage, so force that to 
        happen.
        
        Arguments:   
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None 
          
        Author:
          Nnoduka Eruchalu
        """
        # if there were image files, delete those
        if self.avatar:
            self.delete_avatar_files(self)
            
        
        # get liked rooms for cleanup after delete
        liked_rooms = self.likes.all()
        super(User, self).delete(*args, **kwargs)
        
        # updated likes_count of all liked rooms by forcing saves
        for room in liked_rooms:
            room.save()

class AuthToken(models.Model):
    """
    Blabbit's customized authorization token model.
    Having `key` as primary_key like rest-framework did makes it impossible to
    update it. So I'll make it unique instead
    """
    key = models.CharField(max_length=40, unique=True)
    user = models.OneToOneField(User, related_name='auth_token')
    created = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(AuthToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __unicode__(self):
        return self.key
