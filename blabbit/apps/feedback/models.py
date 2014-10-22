from django.db import models
from django.utils import timezone

# Create your models here.

class Feedback(models.Model):
    """
    User Feedback
    """
    body = models.CharField(max_length=1000)
    email = models.EmailField(max_length=254, blank=True)
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    
    class Meta:
        ordering = ['-date_added']
        
    def __unicode__(self):
        return self.body
