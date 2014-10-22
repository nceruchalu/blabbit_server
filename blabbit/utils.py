"""
Description:
  Utility functions that come in handy through the project

Table Of Contents:
  - slugify:         slugify any given string
  - get_upload_path: determine a unique upload path for a given file
  - list_dedup:      dedup a list and preserve order of elements

Author: 
  Nnoduka Eruchalu
"""

from datetime import datetime
import os, re, unicodedata


def slugify(string):
    """
    Description: Slugify any given string with following rules:
                 - ASCII encoding
                 - Non-alphanumerics are replaced with hyphens
                 - groups of hyphens will be replaced with a single hyphen
                 - slugs cannot begin/end with hyphens.
    
    Arguments:   - string: string to get slugged version of
    Return:      ASCII slugified version of input string
    """
    s = unicode(string)
    # Get normal form 'NFKD' for the unicode version of passed string
    slug = unicodedata.normalize('NFKD', s)
    # Set result to use ASCII encoding
    slug = slug.encode('ascii', 'ignore').lower()
    # Replace all non-alphanumerics with hyphens '-', and strip() any hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    # finally, replace groups of hyphens with a single hyphen
    slug = re.sub(r'[-]+', '-', slug)
    return slug


def get_upload_path(instance, filename, root):
    """
    Description: Determine a unique upload path for a given file
    
    Arguments:   - instance: model instance where the file is being attached
                 - filename: filename that was originally given to the file
                 - root:     root folder to be prepended to file upload path.
                             Example value is 'photo/' or 'photo'  
    Return:      Unique filepath for given file, that's a subpath of `root`
    """
    name = filename.split('.')
    format = slugify(name[0])+"_"+ str(datetime.now().strftime("%Y%m%dT%H%M%S")) + "." + name[len(name)-1]
    return os.path.join(root, format)


def list_dedup(in_list):
    """    
    Description: Dedup a list and preserve order
          
    Arguments:   - in_list: list to have its duplicates removed
    Return:      Dedup'd version of passed list
        
    Author:      Nnoduka Eruchalu
    """
    seen = set()
    return [s for s in in_list if s not in seen and not seen.add(s)]


def human_readable_size(num):
    """
    Description: Present a human readable size size from bytes.
    >>> human_readable_size(2048)
    '2 bytes'
    
    Arguments:
    - num: number of bytes to be converted
    
    Return:
    - A string that represents a human readable size
    
    Ref: http://stackoverflow.com/a/1094933
    """
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')
    
