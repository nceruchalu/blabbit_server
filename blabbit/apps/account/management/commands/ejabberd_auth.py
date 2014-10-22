"""
Authenticate Ejabberd XMPP User
  
The notes on the logic driving this script can be found here:
http://www.ejabberd.im/files/doc/dev.html#htoc9

This is an external authentication script follows the erlang port driver API
[http://www.erlang.org/doc/tutorial/c_portdriver.html].

The script is supposed to do theses actions, in an infinite loop:
  - read from stdin: AABBBBBBBBB.....
    * A: 2 bytes of length data (a short in network byte order)
    * B: a string of length found in A that contains operation in plain text 
         operation are as follows:
      + auth:User:Server:Password (check if a username/password pair is correct)
      + isuser:User:Server (check if it's a valid user)
      + setpass:User:Server:Password (set user's password)
      + tryregister:User:Server:Password (try to register an account)
      + removeuser:User:Server (remove this account)
      + removeuser3:User:Server:Password (remove this account if the password is
          correct)
  - write to stdout: AABB
    * A: the number 2 (coded as a short, which is bytes length of following 
         result)
    * B: the result code (coded as a short), should be 1 for success/valid, or 
         0 for failure/invalid

References:
- http://www.ejabberd.im/node/4000 by Luke Slater and Steve 'Ashcrow' Milner
- https://github.com/ffalcinelli/django-ejabberd-bridge/blob/master/ejabberd_bridge/management/commands/ejabberd_auth.py
"""

import logging, os, struct, sys

from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from blabbit.apps.account.models import User
from django.conf import settings

class Command(BaseCommand):
    """
    Acts as an auth service for ejabberd through ejabberds external auth option.
    See contrib/ejabberd/ejabberd.cfg for an example configuration.
    """
    
    help = "Runs an ejabberd auth service"
    
    def __init__(self, *args, **kwargs):
        """
        Creation of the ejabberd auth bridge service.
        
        Arguments:
          - args:   all non-keywords arguments
          - kwargs: all keyword arguments
        """
        super(Command, self).__init__(*args, **kwargs)
        
        try:
            log_level = int(settings.EJABBERD_AUTH_LOG_LEVEL)
        except:
            log_level = logging.INFO
        
        # ensure logfile directory exists
        log_directory = os.path.dirname(settings.EJABBERD_AUTH_LOG)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        
        # ensure logfile exists
        log_file = open(settings.EJABBERD_AUTH_LOG, 'a+')
        log_file.close()

        # If we can write to the log do so, else fail back to the console
        if os.access(settings.EJABBERD_AUTH_LOG, os.W_OK):
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s %(levelname)s %(message)s',
                filename=settings.EJABBERD_AUTH_LOG,
                filemode='a')
        else:
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s %(levelname)s %(message)s',
                stream=sys.stderr)
            logging.warn(('Could not write to <' +
                settings.EJABBERD_AUTH_LOG +
                '>. Falling back to stderr ...'))
            
        # notify of process start
        logging.info(('ejabberd_auth_bridge process started' +
            ' (more than one is common)'))
       
        
    def from_ejabberd(self, encoding="utf-8"):
        """
        Reads data from stdin as passed by ejabberd
        """
        logging.debug('Attempting to read the data')
        input_length = sys.stdin.read(2).encode(encoding)
        (size,) = struct.unpack('>h', input_length)
        return sys.stdin.read(size).split(':')
    
    def to_ejabberd(self, success=False):
        """
        Creates and sends a response back to the ejabberd server.
 
        Arguments:
          - success: boolean if we should respond successful or not
        """
        answer = 1 if success else 0
        token = struct.pack('>hh', 2, answer).decode("utf-8")
        sys.stdout.write(token)
        sys.stdout.flush()
        logging.debug('Response of %s sent' % (answer,))
        
    def auth(self, username=None, server="localhost", password=None):
        """
        Handles authentication of the user.
 
        Arguments:
          - username: the username to verify
          - server:   the server to verify user on
          - password: the password to verify with the user
        """
        logging.debug("Authenticating %s" % (username,))
        user = authenticate(username=username, password=password)
        return user and user.is_active
        
    def isuser(self, username=None, server="localhost"):
        """
        Check if the user exists and is active
 
        Arguments
          - username: the user name to verify exists
        """
        logging.debug('Attempting to find user: %s' % username)
        try:
            user = User.objects.get(username=username)
            logging.debug('Found user with username: %s' % (username,))
            if user.is_active:
                return True
            else:
                logging.debug('User is disabled: %s' % (username,))
                return False
            
        except User.DoesNotExist:
            logging.debug('No username: %s' % (username,))
            return False
    
    def setpass(self, username=None, server="localhost", password=None):
        """
        Handles user password change
 
        Arguments:
          - username: the username of the user
          - server:   the server the user is on
          - password: the user's new password
        """
        logging.debug("Changing password for %s with new password %s" 
                      % (username, password))
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            return True
        except User.DoesNotExist:
            return False
        
 
    def handle(self, *args, **options):
        """
        Gathers parameters from ejabberd and executes authentication against
        django backend.
 
        Arguments:
          - args:    non-keyword arguments
          - options: keyword arguments
        """
        success = False
        try:
            # Serve forever
            while True:
                data = self.from_ejabberd()
                logging.debug("Operation is: %s" % (data[0],))
                
                # XMPP is expected to provide only lowercase username but
                # for safety force lowercase anyways
                if data[1]:
                    data[1] = data[1].lower()
                    
                # process the operation which came from the ejabberd input
                if data[0] == "auth":
                    success = self.auth(data[1], data[2], data[3])
                elif data[0] == "isuser":
                    success = self.isuser(data[1], data[2])
                elif data[0] == "setpass":
                    success = self.setpass(data[1], data[2], data[3])
                self.to_ejabberd(success)
        
        except Exception as e:
            logging.error("An error occured during ejabberd auth %s" % (e,))
            success = False
            self.to_ejabberd(success)
 
    def __del__(self):
        """
        What to do when we are shut off.
        """
        logging.info('ejabberd_auth process stopped')

