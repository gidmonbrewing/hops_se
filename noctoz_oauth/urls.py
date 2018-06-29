from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
    url(r'^login/$', 'noctoz_oauth.views.facebook_login', name='home'),
)
