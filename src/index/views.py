from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import Context, loader

from index.models import Index


def index(request):
    idx = Index.objects.all()
    t = loader.get_template('index/index.html')
    c = Context({'object_list': idx})
    return HttpResponse(t.render(c))