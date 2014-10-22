"""
Description:
  Manangement command module for purging the database of expired rooms
  
Author: 
  Nnoduka Eruchalu
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from blabbit.apps.conversation.models import Room

from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Delete all expired rooms'
    
    def handle(self, *args, **options):
        """
        Delete all expired rooms and rebuild the search index when done.
        
        Arguments:   *args, **options
        Return:      None
        """
        # get all expired rooms
        earliest_date = timezone.now() - timedelta(
            seconds=settings.ROOM_EXPIRY_TIME_SECONDS)
        expired_rooms = Room.objects.all().filter(created_at__lt=earliest_date)
        
        # delete the expired rooms by calling each object's delete() method
        # as we want all appropriate cleanup to be done.
        for room in expired_rooms:
            room.delete()
        
        # rebuild the index (quietly)
        call_command('rebuild_index', interactive=False, verbosity=0)
        
