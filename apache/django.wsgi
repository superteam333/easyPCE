import os
import sys
 
path = '/srv/www/myapp'
if path not in sys.path:
    sys.path.append(path)
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'myapp.settings'
 
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
