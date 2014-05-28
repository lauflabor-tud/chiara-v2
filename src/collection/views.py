from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import permission_required
from django.core.servers.basehttp import FileWrapper
from exception.exceptions import MissingDescriptionFileException

import os, utils.path, utils.units
import mimetypes
from collection.models import Collection
from collection import webfolder

import logging
from collection.webfolder import get_abs_path
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
    for item_name in webfolder.list_dir(request.user, rel_path):
        rel_item_path = os.path.join(utils.path.no_slash(rel_path), item_name)
        if webfolder.is_file(request.user, rel_item_path):
            file_size = webfolder.get_file_size(request.user, rel_item_path)
            f = webfolder.get_file(request.user, rel_item_path)
            file_revision = f.revision if f else "-" 
            files.append({"name": item_name, 
                          "size": utils.units.convert_data_size(file_size), 
                          "revision": file_revision,
                          "part_of_collection": bool(f)})
        elif webfolder.is_dir(request.user, rel_item_path):
            collection = webfolder.get_collection(request.user, rel_item_path)
            dir_size = webfolder.get_dir_size(request.user, rel_item_path)
            if collection:
                dirs.append({"type": "c",
                             "id": collection.identifier,
                             "name": collection.directory.name, 
                             "size": utils.units.convert_data_size(dir_size), 
                             "revision": collection.revision})
            else:
                d = webfolder.get_dir(request.user, rel_item_path)
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


def operations(request):

    error = False
    post = request.POST
    # unsubscribe collection
    if post["operation"]=="unsubscribe":
        collection = Collection.objects.get(identifier=post["dir_id"], revision=post["dir_revision"])
        collection.unsubscribe(request.user)
        message = "You have successfully unsubsribed the collection '" + collection.directory.name + "'!"
    # remove directory in webfolder
    elif post["operation"]=="remove":
        webfolder.remove_dir_recursive(request.user, utils.path.url_decode(post["rel_dir_path"]))
        message = "You have successfully removed the directory '" + utils.path.url_decode(post["rel_dir_path"]) + "' from your webfolder!"
    # add to repository
    elif post["operation"]=="add":
        try:
            collection = Collection()
            collection.add_to_collection(request.user, utils.path.url_decode(post["rel_dir_path"]))
            message = "You have successfully add the directory '" + utils.path.url_decode(post["rel_dir_path"]) + "' to the repository!"
        except MissingDescriptionFileException:
            message = "No description file found!"
            error = True
    # show commit view for pushing
    elif post["operation"]=="push:commit":
        t = TemplateResponse(request, 'collection/push_commit.html')
        return HttpResponse(t.render())
    # push collection
    elif post["operation"]=="push":
        collection = Collection.objects.get(identifier=post["dir_id"], revision=post["dir_revision"])
        collection.push_local_revision(request.user, utils.path.url_decode(post["rel_dir_path"]))
        message = "You have successfully pushed the local revision of '" + collection.directory.name + "' to the repository!"
    # show revision view for pulling
    elif post["operation"]=="pull:choose_revision":
        collections = Collection.objects.filter(identifier=post["dir_id"])
        t = TemplateResponse(request, 'collection/pull_choose_revision.html',
                             {'dir_name': post["dir_name"],
                              'collections': collections})
        return HttpResponse(t.render())
    # pull collection
    elif post["operation"]=="pull":
        collection = Collection.objects.get(identifier=post["dir_id"], revision=post["revision"])
        collection.download(request.user, os.path.dirname(utils.path.left_slash(utils.path.url_decode(post["rel_dir_path"]))))
        message = "You have successfully updated the collection '" + collection.directory.name + "' to revision " + str(collection.revision) + "!"
    else:
        pass
    
    if error:
        t = TemplateResponse(request, 'error.html',
                             {'message': message})
    else:
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


def download_to_disk(request, rel_file_path):
    abs_file_path = get_abs_path(request.user, rel_file_path)
    download_name =os.path.basename(abs_file_path)
    wrapper = FileWrapper(open(abs_file_path))
    content_type = mimetypes.guess_type(abs_file_path)[0]
    response = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length'] = webfolder.get_file_size(request.user, rel_file_path)   
    response['Content-Disposition'] = "attachment; filename=%s" % download_name
    return response


