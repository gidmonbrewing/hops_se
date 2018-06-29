from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import authenticate, login
import json
import urllib
import urllib2
import urlparse
from urllib2 import HTTPError

def get_user_access_token(request):
	host_url = request.get_host()
	redirect_url = "http://" + host_url + request.path
	page_url = "https://graph.facebook.com/v2.3/oauth/access_token"
	query_data = {
		"client_id": settings.FACEBOOK_APP_ID,
		"redirect_uri": redirect_url,
		"client_secret": settings.FACEBOOK_APP_SECRET,
		"code": request.GET["code"]
	}
	# We create a request with data which will result in a POST
	req = urllib2.Request(page_url, urllib.urlencode(query_data))
	access_token_response = urllib2.urlopen(req)
	access_token_json = access_token_response.read()
	access_token_data = json.loads(access_token_json)
	#print(access_token_data)
	#print("aquired user access token")
	#print(user_access_token["access_token"])

	return access_token_data["access_token"]

def get_app_access_token():
	page_url = "https://graph.facebook.com/oauth/access_token"
	query_data = {
		"client_id": settings.FACEBOOK_APP_ID,
		"client_secret": settings.FACEBOOK_APP_SECRET,
		"grant_type": "client_credentials"
	}
	# We create a request with data which will result in a POST
	req = urllib2.Request(page_url, urllib.urlencode(query_data))
	access_token_response = urllib2.urlopen(req)	
	access_token_json = access_token_response.read()
	#access_token_data = dict(urlparse.parse_qsl(access_token_qs))
	access_token_data = json.loads(access_token_json)
	#print(app_access_token)
	#print("aquired app access token")
	#print(app_access_token["access_token"])
	
	return access_token_data["access_token"]

def validate_access_token(user_access_token):
	page_url = "https://graph.facebook.com/debug_token"
	query_data = {
		"input_token": user_access_token,
		"access_token": settings.FACEBOOK_APP_ID + "|" + settings.FACEBOOK_APP_SECRET
	}
	# The response will be a json object that we need to decode
	debug_token_response = urllib2.urlopen(page_url + "?" + urllib.urlencode(query_data))
	debug_token_json = debug_token_response.read()
	debug_token_dict = json.loads(debug_token_json)
	#print("got debug token data")
	#print(debug_token_dict)
	
	debug_token_data = debug_token_dict["data"]
	app_id = settings.FACEBOOK_APP_ID
	
	return debug_token_data["app_id"] == app_id

def get_user_data(user_access_token):
	page_url = "https://graph.facebook.com/me"
	query_data = {
		"access_token": user_access_token,
	}
	me_response = urllib.urlopen(page_url + "?" + urllib.urlencode(query_data))
	me_json = me_response.read()
	me_data = json.loads(me_json)
	return me_data

def facebook_login(request):
	facebook_page = ""
	if "code" in request.GET:
		try:
			# First we need to get a user access token from the code we got
			user_access_token = get_user_access_token(request)
			#print(user_access_token)
			
			# Verify that the token is valid
			if validate_access_token(user_access_token):
			
				# Get data about the user that we need to login to the site or to create a new user
				user_data = get_user_data(user_access_token)
			
				user = authenticate(user_data=user_data, access_token=user_access_token)
				if user is not None:
					if user.is_active:
						login(request, user)
						return HttpResponseRedirect("/")
					else:
						facebook_page = "User is not active"
				else:
					facebook_page = "Invalid login"
			else:
				facebook_page = "Invalid access token"
		
		#print(json.dumps(debug_token_response, sort_keys = False, indent = 4))
		except HTTPError as e:
			json_error = json.loads(e.read())
			return HttpResponse(json.dumps(json_error, sort_keys = False, indent = 4))
	else:
		query_data = {
			"client_id": settings.FACEBOOK_APP_ID,
			"redirect_uri": "http://" + request.get_host() + request.path,
			"scope": "email"
		}
		login_url = "https://www.facebook.com/dialog/oauth?" + urllib.urlencode(query_data)
		return HttpResponseRedirect(login_url)
	
	return HttpResponse(facebook_page)