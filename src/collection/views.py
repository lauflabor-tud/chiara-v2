from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import Context, loader

from collection.models import Collection

def index(request):
    idx = Collection.objects.all()
    t = loader.get_template('collection/index.html')
    c = Context({'object_list': idx})
    return HttpResponse(t.render(c))