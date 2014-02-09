from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import Context, loader

from collection.models import Collection

def index(request):
    html = """
    <html>
    <body>
        <h2>The django version of chiara is in progress!!</h2>
    </body>
    </html>
    """
    return HttpResponse(html)



def list_collections(request):
    try:
        collections = Collection.objects.all()
    except Collection.DoesNotExist:
        raise Http404
    t = loader.get_template('collection/list_collections.html')
    c = Context({'collections': collections})
    return HttpResponse(t.render(c))