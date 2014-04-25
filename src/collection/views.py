from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required

import os, utils.path, utils.webfolder
from collection.models import Collection

import logging
logger = logging.getLogger(__name__)

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
def my_shared_folder(request, rel_path=''):

    # class the files in category collection, directory or file
    dirs = []
    files = []
    for item_name in utils.webfolder.list_dir(request.user, rel_path):
        rel_item_path = os.path.join(utils.path.no_slash(rel_path), item_name)
        if utils.webfolder.is_file(request.user, rel_item_path):
            file_size = utils.webfolder.get_file_size(request.user, rel_item_path)
            f = utils.webfolder.get_file(request.user, rel_item_path)
            file_revision = f.revision if f else "-" 
            files.append({"name": item_name, 
                          "size": utils.webfolder.convert_size(file_size), 
                          "revision": file_revision,
                          "part_of_collection": bool(f)})
        elif utils.webfolder.is_dir(request.user, rel_item_path):
            collection = utils.webfolder.get_collection(request.user, rel_item_path)
            dir_size = utils.webfolder.get_dir_size(request.user, rel_item_path)
            if collection:
                dirs.append({"type": "c",
                             "id": collection.identifier,
                             "name": collection.directory.name, 
                             "size": utils.webfolder.convert_size(dir_size), 
                             "revision": collection.revision})
            else:
                d = utils.webfolder.get_dir(request.user, rel_item_path)
                dir_revision = d.revision if d else "-"
                dirs.append({"type": "d",
                             "name": item_name, 
                             "size": utils.webfolder.convert_size(dir_size), 
                             "revision": dir_revision, 
                             "part_of_collection": bool(d)})
    
    # call html
    t = TemplateResponse(request, 'collection/my_shared_folder.html', 
                         {'rel_path': utils.path.both_slash(rel_path),
                          'rel_parent_path': utils.path.no_slash(os.path.dirname(rel_path)),
                          'dirs': dirs, 
                          'files': files})
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


