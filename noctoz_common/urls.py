from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
    url(r'^$', 'noctoz_common.views.home', name='home'),
	url(r'news/(?P<news_id>\d+)/$', 'noctoz_common.views.news')
)
