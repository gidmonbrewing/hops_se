from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.contrib.contenttypes.models import ContentType
from beer.models import Review
from noctoz_common.models import NewsItem, Comment
from itertools import chain
from datetime import datetime
import operator
import json
import urllib2

def home(request):
	qs1 = Review.objects.all()
	qs2 = NewsItem.objects.all()
	#test1 = list(chain(qs1, qs2))
	test1 = sorted(chain(qs1, qs2), key = operator.attrgetter('pub_date'), reverse=True)
	#test1 = ContentContainer.objects.all()
	#test1 = ContentContainer.objects.select_related('review', 'newsitem')
	#output = ', '.join([type(p).__name__ for p in test1])
	latest_content = []
	float_right = False
	for content in test1:
		header = ""
		urlstr = ""
		comment_count = 0
		float_class = ""
		newline = False
		if isinstance(content, NewsItem):
			header = "Nyhet: " + content.header
			urlstr = "/noctoz_common/news/" + str(content.id)
		else:
			header = "Recension: " + content.beer.name
			urlstr = "/beer/review/" + str(content.id)
		
		content_type = ContentType.objects.get_for_model(content)
		comments = Comment.objects.filter(content_type__pk=content_type.id, object_id=content.id)
		comment_count = comments.count
			
		if float_right:
			float_class = "float-right"
			float_right = False
			newline = True
		else:
			float_class = "float-left"
			float_right = True
	
		latest_content.append({
			'urlstr': urlstr, 
			'header': header,
			'text': content.text, 
			'author': content.author, 
			'pub_date': content.pub_date,
			'comment_count': comment_count,
			'float_class': float_class,
			'newline': newline,
		})

	facebook_page_data = []

	#if request.user.is_authenticated():
		#if isinstance(request.user, HopsProfile):
		#facebook_profile = request.user.get_profile()
		#page_url = "https://graph.facebook.com/433896706654215/feed?access_token=" # + facebook_profile.access_token
		#facebook_page = json.load(urllib2.urlopen(page_url))
		
		#page_data = facebook_page["data"]
		#for page_entry in page_data:
		#	pub_date = datetime.strptime(page_entry["created_time"], "%Y-%m-%dT%H:%M:%S+0000")
		#	if page_entry["type"] == "link":
		#		facebook_page_data.append({
		#			'pub_date': pub_date,
		#			'message': page_entry["message"],
		#		})
		#	if len(facebook_page_data) == 5:
		#		break

		#facebook_page = json.load(urllib2.urlopen("http://graph.facebook.com/noctoz"))
		#facebook_page = page_url
            
	#t = loader.get_template('first_page.html')
	t = loader.get_template('first_page.html')
	c = RequestContext(request, {
		'latest_content': latest_content,
        'facebook_page': facebook_page_data,
	})
	return HttpResponse(t.render(c))
