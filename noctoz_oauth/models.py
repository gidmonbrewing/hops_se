from django.db import models
from django.contrib.auth.models import User

class FacebookProfile(models.Model):
	id = models.IntegerField(primary_key=True)
	user = models.OneToOneField(User)
	access_token = models.TextField(blank=True, null=True)

	def __unicode__(self):
		return u'FacebookProfile: %s' % (self.user.email)