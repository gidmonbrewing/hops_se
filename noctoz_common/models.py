# encoding: utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms import ModelForm

class ContentStreamItem(models.Model):
	pub_date = models.DateTimeField()
	author = models.ForeignKey(User)
	published = models.BooleanField(default=False)
	thumbnail = models.CharField(max_length=200, blank=True)
	title_img = models.CharField(max_length=200, blank=True)
	
	class Meta:
		abstract = True

class Comment(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField()
	parent_object = generic.GenericForeignKey('content_type', 'object_id')
	pub_date = models.DateTimeField()
	author = models.ForeignKey(User)
	text = models.TextField(blank=True, null=True)
	approved = models.BooleanField(default=False)

	def __unicode__(self):
		return "Comment[%s]: %d %s %s" % (self.content_type, self.object_id, self.author, self.pub_date.strftime("%d %b %Y"))

class CommentForm(ModelForm):
	class Meta:
		model = Comment
		fields = ('text',)

class NewsItem(ContentStreamItem):
	header = models.CharField(max_length=200)
	text = models.TextField()

	def __unicode__(self):
		return self.author.first_name + " " + self.author.last_name + ": " + unicode(self.pub_date)
