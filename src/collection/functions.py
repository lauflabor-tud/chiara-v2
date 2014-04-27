import os
from django.core.exceptions import ObjectDoesNotExist
from collection.models import Directory, Collection, Tag
from authentication.models import UserPermission, Subscription
from utils.enums import Permission
import webfolder.functions as wf_func
from webfolder import collection_info
from exception.exceptions import MissingDescriptionFileException

import logging
logger = logging.getLogger(__name__)


def add_to_collections(user, rel_path):
    """Adds the given user directory to collection repository 
    with all subdirectories and files. Also sets the user permission
    and subscription."""
    try:
        desc_parser = collection_info.parse_description(user, rel_path)
        # Create root directory and save it with all subdirectories and files
        item = os.path.basename(rel_path)
        root_dir = Directory(revision=1,
                             name=item,
                             user_modified=user,
                             size=wf_func.get_dir_size(user, rel_path))
        root_dir.save()
        collection_info.create_traits(user, rel_path, root_dir.id)
        root_dir.save_recursive(user, rel_path)
        
        # Create collection
        collection = Collection(revision=1,
                                directory=root_dir)
        collection.save()
        collection.summary = desc_parser.get_summary()
        collection.details = desc_parser.get_details()
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
    except MissingDescriptionFileException:
        pass
        
        
def unsubscribe(user, collection):
    """Unsubscribe the collection of the user."""
    try:
        subscription = Subscription.objects.get(user=user, collection=collection)
        subscription.delete()
    except ObjectDoesNotExist:
        pass
        