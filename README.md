# Blabbit

## About Blabbit
|         |                                             |
| ------- | ------------------------------------------- |
| Author  | Nnoduka Eruchalu                            |
| Date    | 06/06/2014                                  |
| Website | [http://blabb.it/](http://blabb.it)         |

[Blabbit](http://blabb.it) is a place where anyone can start a chat group. 
All that's required is a 'theme' message to kickstart conversations.
Try this to inspire chatter: 'I dream about fast food daily'.

All conversations and activity happen in  *__realtime__* all thanks to XMPP.

* Chat groups expire after 24 hours of inactivity.
* Groups are always public.
* Messages are anonymous.
* Don't need to login via nickname until ready to create topics.


#### Available on Following Mobile Devices
* [iOS 7+](https://github.com/nceruchalu/blabbit_ios)


## Technologies
* Python
* PostgreSQL
* XMPP  *__[Used for realtime functionality]__*
* Amazon Web Services
* REST
* Javascript
* HTML
* CSS
* [Bootstrap](http://getbootstrap.com)  *__[Used for responsive mobile interface]__*


## Software Description
| Module                    | Description                                      |
| ------------------------- | -------------------------------------------------|
| `settings.py`             | Django settings for project                      |
| `urls.py`                 | URL dispatcher for project                       |
| `utils.py`                | Utility functions useful to multiple Django apps |
| `wsgi.py`                 | WSGI config for Blabbit project                  |
|                           |                                                  |
| **`apps/`**               | Django apps with backend logic                   |
| `apps/account/`           | User account representation and auth. app        |
| `apps/conversation/`      | XMPP room representation  app                    |
| `apps/explore/`           | Exploration of XMPP rooms app.                   |
| `apps/feedback/`          | User feedback app                                |
| `apps/relationship/`      | XMPP roster representation app                   |
| `apps/rest/`              | [django rest framework](https://github.com/tomchristie/django-rest-framework) customizations |
| `apps/search/`            | Search engine integration app                   |
|                           |                                                  |
| **`static/`**             | static files for project                         |
| `static/css/`             | CSS files                                        |
| `static/img`              | Static images                                    |
| `static/js/`              | Javascript files                                 |
|                           |                                                  |
| **`templates/`**          | Django templates used by apps                    |
| `templates/404.html`      | 404 page                                         |
| `templates/500.html`      | 500 page                                         |
| `templates/base.html`     | base template used by all templates              |
| `templates/account`       | templates used by `account` app's views          |
| `templates/rest_framework`|templates used for customizing browseable REST API|
| `templates/search`        | templates used for generating search indexes     |


### 3rd-party Python Modules
* [django](https://www.djangoproject.com/)
* [whoosh](https://bitbucket.org/mchaput/whoosh/wiki/Home)

###### The following modules have been saved in a local folder on PYTHONPATH
* [django imagekit](https://github.com/matthewwithanm/django-imagekit)
    * depends on [pilkit](https://github.com/matthewwithanm/pilkit)
    * depends on [django-appconf](https://github.com/jezdez/django-appconf)
        * depends on [six](https://pypi.python.org/pypi/six)
* [django storages](https://bitbucket.org/david/django-storages/overview)
    * specifically S3.py which
        * depends on [python-boto](https://github.com/boto/boto)
* [django haystack](https://github.com/toastdriven/django-haystack)
* [django rest framework](https://github.com/tomchristie/django-rest-framework)
    * depends on [django-filter](https://github.com/alex/django-filter)
    * depends on [Markdown](https://pypi.python.org/pypi/Markdown/)


#### 3rd-party Javascript Modules
* [jQuery](http://jquery.com/) 


#### 3rd-party HTML template
* [Landy](https://github.com/paolotripodi/Landy-v1.0) for a quick and easy app landing page.


### Design Decisions

#### REST API
##### Resource Identifiers
Publicly exposed identifiers (IDs), such as those exposed in RESTful URLs,
should not expose (or rely on) underlying technology. 
I considered using the model pks as the resource identifier. These pks are currently Postgres serial fields. A database migration would change these pks significantly. Also fact is that ejabberd references objects (user and rooms) by their unique names, so I chose to be consistent with ejabberd.

This [article here](http://toddfredrich.com/ids-in-rest-api.html) gives a better explanation of what to use as resource identifiers.


#### Database
##### User accounts
To give Django total control over authentication ejabberd is configured for external authentication.


##### Ejabberd roster and user relationships
There are two ways to represent user relationships in the database:

1. Ejabberd roster table is read-write for ejabberd, and read-only for django.
  Use the ejabberd `rosterusers` table and all roster modifications are done by ejabberd.
  * The upside is that changes in roster will be seen immediately by connected users. 
  * The downside is not having nickname coming straight from the django `account_user` table. We will either need another client call to the server to get all nicknames for given userJIDs or have django or a DB-trigger duplicate this information across multiple `rosterusers` table rows.

2. Ejabberd roster table is a read-only view for ejabberd, and read-write for django
  Setup a custom relationship table and make `rosterusers` a read-only view. All roster modifications are done by django. 
  * The upside to this is that the `rosterusers` view will have efficient access to the nicknames and this will be pulled as a part of the view's query.
  * The downside is that changes in roster won't be seen immediately by connected users unless django informs ejabberd about that via [roster push](http://xmpp.org/rfcs/rfc6121.html#roster-syntax-actions-push).

###### Selected approach
I've chosen to go with *__option (1)__* and let `rosterusers` be a read-write table.
The reason for this is I want friend requests, deletions to happen in realtime and not depend on any status changes.
The nickname field will be be pulled by a separate client call to the server.


##### Groupchats/Rooms
Django and ejabberd will share read/write access to the `muc_room` table expected by ejabberd. 
Django will extend the schema expected by ejabberd so as to provide extra fields like participants, owner, photo and location.


## Deployment

### GeoDjango
#### Installation
Mostly following the steps in the [geodjango installation guide](https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/#ref-gis-install).
Install the following geospatial libraries:
* GEOS
* PROJ.4
* GDAL
* PostGIS

#### Database Setup
Create the database and make it a spatial database with the following commands 
(specific to Postgist 2.0 and Postgresql9.1+)
```
$ createdb <db name> -O <owner_username> -U <owner_username>
$ psql <db name> -U <owner_username>
> CREATE EXTENSION postgis;
> CREATE EXTENSION postgis_topology; [This is optional]
```

The `CREATE EXTENSION postgis` command is only available for version 2.0.0 and above. Webfaction currently has version 1.5.3 so be sure to enable PostGis during database creation else life will be difficult.
This command should create following relations so be sure they exist:
 Schema |       Name        | Type  |      Owner       
--------+-------------------+-------+------------------
 public | geography_columns | view  | <owner_username>
 public | geometry_columns  | view  | <owner_username>
 public | raster_columns    | view  | <owner_username>
 public | raster_overviews  | view  | <owner_username>
 public | spatial_ref_sys   | table | <owner_username>


### Ejabberd Configuration
#### Configure external authentication
In ejabberd's config file select external authenticaiton and provide the path
to our script

```
%%
%% Authentication using external script
%% Make sure the script is executable by ejabberd.
%%
{auth_method, external}.
{extauth_program, "/path/to/ejabberd_auth_script.sh"}.
```

This script must be made executable (`chmod +x`). 
It simply calls the django command to perform authentication.


#### Configure ejabberd with PostgreSQL native driver
First download the [PostgreSQL database schema] (https://github.com/processone/ejabberd/blob/master/sql/pg.sql)
```
wget https://raw.githubusercontent.com/processone/ejabberd/master/sql/pg.sql
```

Import ejabberd database schema into the ejabberd database:
```
\i /path/to/pg.sql
```

Drop the tables `rosterusers` and `muc_room`. They will be recreated by django's
`syncdb` command.

Use both anonymous and external authentication. This of course requires setting
up odbc_server in the ejabberd configuration

Go through all modules in ejabberd.yml and change the persistence settings from Mnesia to odbc.


### Django Setup: 

#### Settings files
The Django project is missing the `blabbit/settings_secret.py` file. A template version is included for help in setting up the sensitive information needed by the project.

#### Database Setup
Run `syncdb` to create necessary tables and replace the dropped `rosterusers` and `muc_room` tables.


#### 3rd party libraries
* Modified rest_framework.compat markdown module to use the 'tables' extension
  with following line
 ```
 extensions = ['headerid(level=2)', 'tables']
 ```

### Server Setup Notes
These instructions here are what I did on my [Webfaction](https://www.webfaction.com/) server.


#### `httpd.conf` Additions:
Add the following lines to ensure all requests to [www.blabb.it](http://www.blabb.it) are redirected to [blabb.it](http://blabb.it).

```
LoadModule alias_module      modules/mod_alias.so

RewriteEngine on
RewriteCond %{HTTP_HOST} ^www\.blabb\.it [NC]
RewriteRule ^(.*)$ http://blabb.it$1 [L,R=301]
```

Since we are using Apache & mod_wsgi, add this line at the end of the conf file,
after `WSGIScriptAlias / ...`
```
WSGIPassAuthorization On
```
See [this post](http://dustindavis.me/basic-authentication-on-mod_wsgi.html) for details.


#### Crontab Additions
Access crontab with:
```
crontab -e
```

Edit it to perform following functionality:

* Setup PATH, PYTHONPATH to be used by cron's environment
* Restart apache every 30 minutes. This ensures minimal downtime (if at all)
* Run management command to update search indexes every 45 minutes.
* Backup database daily using configurations hidden in config file [some values redacted]

```
PATH=/home/nceruchalu/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:.
PYTHONPATH=/home/nceruchalu/lib/python2.7:/home/nceruchalu/pythonlibs:/home/nceruchalu/webapps/blabbit:/home/nceruchalu/webapps/blabbit/blabbit

12,32,52 * * * * ~/webapps/blabbit/apache2/bin/start
*/45 * * * * /usr/local/bin/python2.7 ~/webapps/blabbit/blabbit/manage.py update_index > ~/cron/blabbit_update_index.log 2>&1
10 */4 * * * /usr/local/bin/python2.7 ~/webapps/blabbit/blabbit/manage.py purge_expired_rooms
*/5 * * * * sh ~/cron/watchdog_ejabberd.sh > ~/cron/watchdog_ejabberd.log 2>&1
0 2 * * * mysqldump --defaults-file=$HOME/db_backups/<config-filename>.cnf -u <username> <database> > $HOME/db_backups/<backups-root-filename>-`date +\%Y\%m\%d`.sql 2>> $HOME/db_backups/cron.log
```

###### Ejabberd Watchdog Script
The ejabberd watchdog script is to keep the ejabberd server always running.
This is the XMPP server for which downtime isn't acceptable. This script assumes `ejabberdctl`'s `EJABBERD_PID_PATH` variable is configured appropriately
```
#!/usr/bin/env bash

PIDFILE="$HOME/pid/ejabberd.pid"

if [ -e "${PIDFILE}" ] && (ps -u $(whoami) -f | grep "[ ]$(cat ${PIDFILE})[ ]"); then
  echo "Already running."
  exit 99
fi

$HOME/sbin/ejabberdctl start
```

#### Installing ejabberd and dependencies 
Follow these steps to install from source on Webfaction:

* `wget <archive url>`
* `tar -xzvf <compressed arhive>`
* `cd <archive folder>`
* `./configure --prefix=$HOME`
  * For ejabberd be sure to configure with `./configure --prefix=$HOME --enable-odbc --enable-mysql --enable-pgsql --enable-zlib --enable-debug --enable-lager --enable-tools --enable-user=<Username here>`
  * Again for ejabberd only, follow this up with `./rebar get-deps`
* `make`
* `make install`

These require following bash_profile configurations
```
export PATH=$PATH:$HOME/bin:$HOME/sbin
export LD_LIBRARY_PATH=$HOME/lib
export LIBRARY_PATH=$HOME/lib
export C_INCLUDE_PATH=$C_INCLUDE_PATH:$HOME/include
```
We use `LIBRARY_PATH` because `LD_LIBRARY_PATH` doesn't do the trick
We add `$HOME/sbin` because that's where `ejabberdctl` is installed


##### Ejabberd Makefile Bug Warning
Ejabberd 14.05 adn 14.07 have a [bug where the Makefile.in removes configure.beam](https://support.process-one.net/browse/EJAB-1710) with the following statement:
```
rm -f $(BEAMDIR)/configure.beam
```
This prevents ejabberd from starting. 
Edit the ejabberd Makefile.in to comment out this line.


##### Ejabberd configuration file
Configuration file located at '$HOME/etc/ejabberd/ejabberd.yml'


## Miscellaneous

#### To Run Development Server
```
python manage.py runserver 0:8000
```

#### To Make REST API calls from command line
Sample HTTP POST:
```
curl -d "key1=param1&key2=param2" -X POST http://localhost:8000/api/path/
```

Here's one that requires an authentication:
curl -H "Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a" -d "key1=param1&key2=param2" -X POST http://localhost:8000/api/path/

Here's another that specifies content type:
curl -H "Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a" -H "Content-type: application/json" -d '{"key":"value"}' -X PUT http://localhost:8000/api/path/


#### TODO
* [REST API Throttling](http://www.django-rest-framework.org/api-guide/throttling)
* REST API base URL should be [api.blabb.it](https://api.blabb.it)