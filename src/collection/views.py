from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required

from collection.models import Collection

def index(request):
    t = TemplateResponse(request, 'base.html', {})
    return HttpResponse(t.render())


def news(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'collection/news.html', 
                         {'collections': collections})
    return HttpResponse(t.render())


@permission_required('collection.my_shared_folder', login_url="/login/")
def my_shared_folder(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'collection/my_shared_folder.html', 
                         {'collections': collections})
    return HttpResponse(t.render())


def retrieve_new_collections(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'collection/retrieve_new_collections.html', 
                         {'collections': collections})
    return HttpResponse(t.render())


@permission_required('collection.manage_my_collections', login_url="/login/")
def manage_my_collections(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'collection/manage_my_collections.html', 
                         {'collections': collections})
    return HttpResponse(t.render())
