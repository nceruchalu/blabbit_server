from django.contrib.gis.db import models
from blabbit.apps.account.models import User

from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, Adjust
from blabbit.utils import get_upload_path

from django.utils import timezone

# Create your models here.

# HELPER FUNCTIONS
def get_room_photo_path(instance, filename):
    return get_upload_path(instance, filename, 'img/r/')

class Room(models.Model):
    """
    Table representing each Multi-User chat room. This table is read/write
    for both Django and Ejabberd server. Note that ejabberd does creates and
    updates while django only does updates.
    
    The default ejabberd `muc_room` schema is extended here for extra Blabbit 
    functionality. These extra fields will be ignored by ejabberd when it
    creates room entries so these fields have to allow NULL values.
    
    There's a django standard that suggests we avoid using NULL on string-based 
    fields such as CharField and TextField because empty string values will 
    always be stored as empty strings, not as NULL so `subject` and `photo` will
    be set to have defaults of '' in the custom SQL script `sql/room.sql`.
    """
    # DEFAULT SCHEMA FIELDS
    # room name i.e. localpart of room's JID, <localpart>@<domainpart>
    name = models.TextField()
    
    # room host i.e. domain part of room's JID, <localpart>@<domainpart>
    host = models.TextField()
    
    # room configuration options
    opts = models.TextField()
    
    # date when room was created
    created_at = models.DateTimeField(default=timezone.now)
    
    
    # EXTENDED SCHEMA FIELDS
    # owner of the chat room.
    owner = models.ForeignKey(User, related_name="owned_rooms", null=True, 
                              blank=True)
    
    # members of the chat room.
    members = models.ManyToManyField(User, related_name="rooms", null=True,
                                     blank=True)
    
    # chat room likes.
    likes = models.ManyToManyField(User, related_name="likes", null=True,
                                     blank=True)
    # keep this stat so we wont have to run a count() query each time we want
    # to get the number of likes on a room. We need this value to always be
    # valid so it cannot be set to NULL but will instead have a default of 0
    likes_count = models.IntegerField(default=0, blank=True)
    
    # room subject
    subject = models.CharField(max_length=200, blank=True)
    
    # room's optional representative photo
    photo =  models.ImageField(upload_to=get_room_photo_path, blank=True)
    
    # imagekit spec for avatar shown in mobile app's Conversation UITableView
    photo_thumbnail = ImageSpecField(
        source='photo',
        processors=[SmartResize(width=120, height=120),
                    Adjust(contrast = 1.2, sharpness=1.1)],
        format='JPEG',
        options={'quality':90})
    
    # this is used for tracking photo changes
    # ref: http://stackoverflow.com/a/1793323
    __original_photo = None
    
    # last modified date to be used by client apps for sync purposes.
    # for this reason it will not have null=True even though it's an extension
    # of ejabberd's default schema. So it will have an SQL-level default set
    # ref: http://stackoverflow.com/a/5052208
    last_modified = models.DateTimeField(auto_now=True)
    
    # GeoDjango-specific:a geography field (PointField) for room creation 
    # location, and overriding the default manager with a GeoManager instance to
    #   perform spatial queries
    location = models.PointField(geography=True, null=True, blank=True)
    objects = models.GeoManager() 
    
    class Meta:
        db_table = 'muc_room'
        ordering = ['-created_at'] 
    
    
    def __unicode__(self):
        return self.name
    
    def __init__(self, *args, **kwargs):
        super(Room, self).__init__(*args, **kwargs)
        self.__original_photo = self.photo
        
    def get_photo_thumbnail_url(self):
        """
        get url of photo's thumbnail. If there isn't a photo_thumbnail then
        return an empty string
        """
        return self.photo_thumbnail.url if self.photo_thumbnail else ''
        
    def delete_photo_files(self, instance):
        """
        Delete an room's photo files in storage
        - First delete the room's ImageCacheFiles on storage. The reason this 
          must happen first is that deleting source file deletes the associated 
          ImageCacheFile references but not the actual ImageCacheFiles in 
          storage.
        - Next delete source file (this also performs a delete on the storage 
          backend)
                
        Arguments:   
          - instance: Room object instance to have files deleted
        Return:
          None 
        """
        # get photo_thumbnail location and delete it
        instance.photo_thumbnail.storage.delete(instance.photo_thumbnail.name)
        # delete photo
        instance.photo.delete()
        
    def save(self, *args, **kwargs):
        """
        On instance save ensure old image files are deleted if images are 
        updated.
                            
        Arguments:   
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None 
        """
        if self.__original_photo and self.photo != self.__original_photo:
            # photo has changed and this isn't the first photo upload, so delete
            # old files
            orig = Room.objects.get(pk=self.pk)
            self.delete_photo_files(orig)
            
        # update likes count
        try:
            self.likes_count = self.likes.count()
        except:
            pass
        
        super(Room, self).save(*args, **kwargs)
        self.__original_photo = self.photo
            
    
    def delete(self, *args, **kwargs):
        """
        Default model delete doesn't delete files on storage, so force that to 
        happen.
        
        Arguments:   
          - args: all positional arguments
          - kwargs: all keyword arguments
        Return:
          None
        """
        if self.photo:
            self.delete_photo_files(self)
        
        super(Room, self).delete(*args, **kwargs)


class RoomFlag(models.Model):
    """
    Records a flag on a room.
    A flag could be:
    * A "removal suggestion" -- where a user suggests a room for (potential) 
      removal.
    * A "moderator deletion" -- used when a moderator deletes a comment.
    
    By design users are only allowed to flag a comment with a given flag once.
    
    This is based off django contrib comments library.
    """
    user = models.ForeignKey(User, related_name="room_flags", null=True, 
                             blank=True)
    room = models.ForeignKey(Room, related_name="flags")
    
    # Constants for flag types
    SUGGEST_REMOVAL = "removal suggestion"
    MODERATOR_DELETION = "moderator deletion"
    MODERATOR_APPROVAL = "moderator approval"
    
    FLAG_CHOICES = (
        (SUGGEST_REMOVAL,    "Removal suggestion"),
        (MODERATOR_DELETION, "Moderator deletion"),
        (MODERATOR_APPROVAL, "Moderator approval"),
        )
    
    flag = models.CharField(max_length=30, db_index=True, choices=FLAG_CHOICES,
                            default=SUGGEST_REMOVAL)
    flag_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-flag_date']
        unique_together = [('user', 'room', 'flag')]
        verbose_name = 'room flag'
        verbose_name_plural = 'room flags'
        
    def __unicode__(self):
        return self.room.subject
