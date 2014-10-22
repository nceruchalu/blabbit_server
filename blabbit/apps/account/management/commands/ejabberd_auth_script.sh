#!/bin/bash


if [ "$HOSTNAME" = Nnodukas-MacBook-Pro.local ]; then
    
    # Mac OSX Exports for development machine
    # export path to python (/opt/local/bin/) and postgresql binaries
    export PATH=/opt/local/bin:/opt/local/lib/postgresql93/bin
    
    # on MacOSX also need to set DYLD FALLBACK PATH as a replacement for the
    # UNIX LD_LIBRARY_PATH environment variable, so that geodjango knows where
    # to find the shared libraries (e.g., for GEOS (libgeos) and GDAL(libgdal)).
    export DYLD_FALLBACK_LIBRARY_PATH=/opt/local/lib:/opt/local/lib/postgresql93
    
    python2.7 ~/Documents/django/blabbit/manage.py ejabberd_auth $@
    
else
    
    # UNIX exports for production machine
    # export path to python (/usr/local/bin/) and postgres binaries (/usr/bin/)
    export PATH=/usr/local/bin:/usr/bin
    
    # just like on MacOSX need to set LD_LIBRARY_PATH, so that geodjango knows
    # where to find the shared libraries
    export LD_LIBRARY_PATH=$HOME/lib
    
    python2.7 ~/webapps/blabbit/blabbit/manage.py ejabberd_auth $@
fi



