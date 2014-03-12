from django.http import HttpResponse, Http404
from django.template import Context, loader
from django.template.response import TemplateResponse

from collection.models import Collection

def index(request):
    t = TemplateResponse(request, 'base.html', {})
    return HttpResponse(t.render())


def news(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('collection/news.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))


def my_shared_folder(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('collection/my_shared_folder.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))


def retrieve_new_collections(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('collection/retrieve_new_collections.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))


def manage_my_collections(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('collection/manage_my_collections.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))
