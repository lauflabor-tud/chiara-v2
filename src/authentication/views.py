from django.http import HttpResponse, Http404
from django.template import Context, loader

from collection.models import Collection

def my_account(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('authentication/my_account.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))