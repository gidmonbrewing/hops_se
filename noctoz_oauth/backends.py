from django.contrib.auth.models import User
from noctoz_oauth.models import FacebookProfile

class OAuthBackend(object):
    def authenticate(self, user_data, access_token):
		print("Authenticating OAuth User")
		try:
			user = User.objects.get(email=user_data["email"])
		except User.DoesNotExist:
			print("User did not exist, creating new")
			user = User(username=user_data["username"], password=User.objects.make_random_password(length=40))
			user.email = user_data["email"]
			user.first_name = user_data["first_name"]
			user.last_name = user_data["last_name"]
			user.save()
		
		try:
			profile = FacebookProfile.objects.get(id = user_data["id"])
		except FacebookProfile.DoesNotExist:
			print("Creating FacebookProfile")
			profile = FacebookProfile(id=user_data["id"], user=user)
			profile.access_token = access_token
			profile.save()
		
		return user
	
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None