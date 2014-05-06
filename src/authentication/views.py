from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.views import login as contrib_login, logout as contrib_logout

from collection.models import Collection

def preferences(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'authentication/preferences.html', 
                     {'collections': collections})
    return HttpResponse(t.render())


def login(request):
    return contrib_login(request, template_name='authentication/login.html')


def logout(request):
    return contrib_logout(request, template_name='authentication/logout.html')