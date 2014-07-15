import logging

from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.utils import timezone

from log.models import News
from collection.models import Collection

from datetime import timedelta

logger = logging.getLogger(__name__)

def news(request):
    try:
        if request.POST.get("date_filter"):
            date_filter = int(request.POST.get("date_filter"))
        else:
            date_filter = 10
        last_date = timezone.now()-timedelta(days=date_filter)
        
        if request.user.is_anonymous():
            news = [n for n in News.objects.order_by("-date")
                    if (n.collection!=None and n.collection.public_access) # user news (public collection)
                    and (n.date>=last_date)]
        else:
            news = [n for n in News.objects.order_by("-date")
                    if ((n.collection==None and n.group==None) # general news
                    or  (n.collection!=None and n.collection.public_access) # user news (public collection)
                    or  (n.collection!=None and n.collection in request.user.permissions.all()) # user news (collection)
                    or  (n.group!=None and n.group in request.user.groups.all())) # user news (group)
                    and (n.date>=last_date)]
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'log/news.html',
                         {'news': news,
                          'date_filter': date_filter})
    return HttpResponse(t.render())