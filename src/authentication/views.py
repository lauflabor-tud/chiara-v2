from django.http import StreamingHttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.views import login as contrib_login, logout as contrib_logout
from django.contrib.auth.views import password_change as contrib_password_change, password_change_done as contrib_password_change_done

from collection.models import Collection

def preferences(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = TemplateResponse(request, 'authentication/preferences.html', 
                     {'collections': collections})
    return StreamingHttpResponse(t.render())


def login(request):
    return contrib_login(request, template_name='authentication/login.html')


def logout(request):
    return contrib_logout(request, template_name='authentication/logout.html')


def password_change(request):
    return contrib_password_change(request, template_name='authentication/password_change.html')


def password_change_done(request):
    return contrib_password_change_done(request, template_name='authentication/password_change_done.html')