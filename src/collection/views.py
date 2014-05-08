from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required

import os, utils.path, utils.units
from collection.models import Collection
import webfolder.functions as wf_func
import collection.functions as col_func

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

    # class the files in categories collection, directory or file
    dirs = []
    files = []
    for item_name in wf_func.list_dir(request.user, rel_path):
        rel_item_path = os.path.join(utils.path.no_slash(rel_path), item_name)
        if wf_func.is_file(request.user, rel_item_path):
            file_size = wf_func.get_file_size(request.user, rel_item_path)
            f = wf_func.get_file(request.user, rel_item_path)
            file_revision = f.revision if f else "-" 
            files.append({"name": item_name, 
                          "size": utils.units.convert_data_size(file_size), 
                          "revision": file_revision,
                          "part_of_collection": bool(f)})
        elif wf_func.is_dir(request.user, rel_item_path):
            collection = wf_func.get_collection(request.user, rel_item_path)
            dir_size = wf_func.get_dir_size(request.user, rel_item_path)
            if collection:
                dirs.append({"type": "c",
                             "id": collection.identifier,
                             "name": collection.directory.name, 
                             "size": utils.units.convert_data_size(dir_size), 
                             "revision": collection.revision})
            else:
                d = wf_func.get_dir(request.user, rel_item_path)
                dir_revision = d.revision if d else "-"
                dirs.append({"type": "d",
                             "name": item_name, 
                             "size": utils.units.convert_data_size(dir_size), 
                             "revision": dir_revision, 
                             "part_of_collection": bool(d)})
    
    # call html
    t = TemplateResponse(request, 'collection/my_shared_folder.html', 
                         {'rel_path': utils.path.both_slash(rel_path),
                          'rel_parent_path': utils.path.no_slash(os.path.dirname(rel_path)),
                          'dirs': dirs, 
                          'files': files})
    return HttpResponse(t.render())


def action(request, rel_path, dir_name):
    action = request.POST["listdir-action"]
    dir_path = os.path.join(rel_path, dir_name)
    if action=="unsubscribe":
        collection = wf_func.get_collection(request.user, dir_path)
        col_func.unsubscribe(request.user, collection)
        message = "You have successfully unsubsribed the collection '" + dir_name + "'!"
    elif action=="remove":
        col_func.remove_from_webfolder(request.user, dir_path)
        message = "You have successfully removed the directory '" + dir_path + "' from your webfolder!"
    elif action=="add":
        col_func.add_to_collections(request.user, dir_path)
        message = "You have successfully add the directory '" + dir_path + "' to the repository!"
        pass
    elif action=="push":
        pass
    elif action=="pull":
        pass
    else:
        pass
    
    t = TemplateResponse(request, 'info.html', 
                         {'message': message})
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


