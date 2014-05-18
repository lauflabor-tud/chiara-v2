import os
from django.core.exceptions import ObjectDoesNotExist
from collection.models import Directory, Collection, Tag
from authentication.models import UserPermission, Subscription
from utils.enums import Permission
import webfolder.functions as wf_func
from webfolder import collection_info

import logging
logger = logging.getLogger(__name__)


def add_to_collections(user, rel_path):
    """Adds the given user directory to collection repository 
    with all subdirectories and files. Also sets the user permission
    and subscription."""
    desc_parser = collection_info.parse_description(user, rel_path)
    # Create root directory and save it with all subdirectories and files
    item = os.path.basename(rel_path)
    root_dir = Directory(revision=1,
                         name=item,
                         user_modified=user,
                         size=wf_func.get_dir_size(user, rel_path))
    root_dir.save()
    collection_info.create_traits(user, rel_path, root_dir.identifier)
    root_dir.save_recursive(user, rel_path)
    
    # Create collection
    collection = Collection(revision=1,
                            directory=root_dir)
    collection.save()
    collection.summary = desc_parser.get_summary()
    collection.details = desc_parser.get_details()
    collection.comment = "Add the collection to the repository."
    collection.save()
    for (key,value) in desc_parser.get_tags():
        tag = Tag(key=key, value=value)
        tag.save()
        collection.tags.add(tag)

    # Set user access
    permission = UserPermission(collection=collection,
                                user=user,
                                permission=Permission.WRITE)
    permission.save()
    collection.authors.add(user)
    
    # Set user subscription
    subscription = Subscription(collection=collection,
                                user=user)
    subscription.save()
        

def remove_from_webfolder(user, rel_path):
    """Deletes the directory from webfolder"""
    wf_func.remove_dir_recursive(user, rel_path)


def unsubscribe(user, collection):
    """Unsubscribe the collection of the user."""
    try:
        subscription = Subscription.objects.get(user=user, collection=collection)
        subscription.delete()
    except ObjectDoesNotExist:
        pass
    

def push_local_revision():
    pass


def update_to_revision():
    pass
        
