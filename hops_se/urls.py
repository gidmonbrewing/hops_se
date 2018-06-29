from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Examples:
    url(r'^$', 'hops_se.views.home', name='home'),
    # url(r'^hops_se/', include('hops_se.foo.urls')),

    #static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    #static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name='auth_login'),
	url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    
    url(r'^beer/$', 'beer.views.index'),
    url(r'^beer/(?P<beer_id>\d+)/$', 'beer.views.beer'),
    url(r'^beer/brewery/(?P<brewery_id>\d+)/$', 'beer.views.brewery'),
    url(r'^beer/review/(?P<review_id>\d+)/$', 'beer.views.review'),
	url(r'^beer/recipe/$', 'beer.views.recipes'),
	url(r'^beer/recipe/(?P<recipe_id>\d+)/$', 'beer.views.recipe'),
	url(r'^beer/add_beer/$', 'beer.views.add_beer'),
	url(r'^beer/add_brewery/$', 'beer.views.add_brewery'),
	url(r'^beer/add_town/$', 'beer.views.add_town'),
	url(r'^beer/recipe/add_comment/(?P<recipe_id>\d+)/$', 'beer.views.recipe_add_comment'),

	#url(r'^facebook/', include('django_facebook.urls')),
	#url(r'^accounts/', include('django_facebook.auth_urls')),
	#url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='auth_login'),
	#url(r'^logout/$', auth_views.logout, name='auth_logout'),/
	url(r'^noctoz_common/', include('noctoz_common.urls')),
	url(r'^auth/', include('noctoz_oauth.urls')),
)
