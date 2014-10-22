from django.db import models
from blabbit.apps.account.models import User

from django.utils import timezone

# Create your models here.

class Friendship(models.Model):
    """
    Table representing each 2-way friendship by two 1-way relationships.
    This table is read-only from Django's point of view. Ejabberd server
    will do all writing to the table.
    """
    
    # user who is doing the following
    # purposely setting the db_index to False as this will be handled with
    # custom SQL 
    username = models.ForeignKey(User, related_name="followings",
                                 db_column="username", to_field="username",
                                 db_index=False)
    # jid of followed user
    jid = models.TextField()
    # nickname of the followed user. This should be sync'd with User.first_name
    nick = models.TextField()
    
    # subscription status:
    #   N = None; T = True; F = From; B = Both
    subscription = models.CharField(max_length=1)
    
    # subscription ask:
    #   N = None; O = Pending Out; I = Pending In; 
    #   B = Both, U = Unsubscribe; S = subscribe
    ask = models.CharField(max_length=1)
    
    # askmessage. Not used here
    askmessage = models.TextField()
    
    # server. Always seems set to 'N'
    server = models.CharField(max_length=1)
    
    # subscribe.
    subscribe = models.TextField(null=True)
    
    # type. Always set to 'item'
    type = models.TextField(null=True)
    
    # date when relationship was started.
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'rosterusers'
    
    def __unicode__(self):
        """
        String representation of each 1-way relationship.
        """
        return u'%s -> %s: s:%s, a:%s' % (self.username, self.jid, 
                                          self.subscription, self.ask)
    
    def save(self, *args, **kwargs):
        """
        This table is read-only for Django so override the save method to do
        nothing
        
        Arguments:   
          - args:   positional arguments
          - kwargs: keyword arguments
        Return:     
          None
        """
        pass
    
    def delete(self, *args, **kwargs):
        """
        This table is read-only for Django so override the delete method to do
        nothing.
        
        Arguments:   
          - args:   positional arguments
          - kwargs: keyword arguments
        Return:     
          None
        """
        pass
