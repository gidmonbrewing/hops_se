from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from noctoz_common.models import NewsItem, Comment, CommentForm
import datetime

def home(request):
	page_data = "This will hold comment system etc"
	
	return HttpResponse(page_data)

def news(request, news_id):
	news = NewsItem.objects.get(id=news_id)
	
	if request.method == 'POST':
		try:
			comment = Comment(parent_object=news, author=request.user, pub_date=datetime.datetime.now())
			comment.save()
			edited_form = CommentForm(request.POST, instance=comment)
			edited_form.save()
		except Exception as e:
			return HttpResponse(e)

	news_type = ContentType.objects.get_for_model(news)
	comments = Comment.objects.filter(content_type__pk=news_type.id, object_id=news.id)
	comment_form = CommentForm()
	
	t = loader.get_template("content_stream/news.html")
	c = RequestContext(request, {
		'news': news,
		'comments': comments,
		'comment_form': comment_form,
	})
	return HttpResponse(t.render(c))