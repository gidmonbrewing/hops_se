import os, sys

#f = open("/tmp/check", "w")
#f.write("TEST!!!!!#!#")
#f.close()

#sys.path.insert(0, '/srv/sites/hops_se')
#sys.path.append('/usr/local/lib/python2.7/dist-packages')

#from django.conf import settings
#settings.configure(LOG_DATE_FORMAT = '%d %b %Y %H %M % S')

os.environ['DJANGO_SETTINGS_MODULE'] = 'hops_se.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
