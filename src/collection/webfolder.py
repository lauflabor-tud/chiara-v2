import os, shutil, ConfigParser
from chiara.settings.common import WEBDAV_DIR, COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE, COLLECTION_TRAITS_FILE, REPOSITORY_DIR
import utils.path

traits_parser = ConfigParser.RawConfigParser()

import logging
logger = logging.getLogger("webfolder")

def get_abs_path(user, rel_path):
    return os.path.join(WEBDAV_DIR, user.user_name, utils.path.no_slash(rel_path))


def list_dir(user, rel_path):
    return os.listdir(get_abs_path(user, rel_path))


def is_file(user, rel_path):
    return os.path.isfile(get_abs_path(user, rel_path))


def is_dir(user, rel_path):
    return os.path.isdir(get_abs_path(user, rel_path))


def is_collection(user, rel_path):
    abs_path = get_abs_path(user, rel_path)
    if(os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_DESCRIPTION_FILE)) and
       os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))):
        traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return bool(user.subscriptions.filter(identifier=traits_parser.get('Common', 'id')))
    else:
        return False
    

def get_collection_of_item(user, rel_path):
    rel_path = utils.path.no_slash(rel_path)
    abs_path = get_abs_path(user, rel_path)
    if (rel_path=="" or not os.path.exists(abs_path)):
        return None
    elif is_collection(user, rel_path):
        traits_parser.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return user.subscriptions.get(identifier=traits_parser.get('Common', 'id'))
    else:
        return get_collection_of_item(user, os.path.split(rel_path)[0])


def get_collection(user, rel_path):
    if is_collection(user, rel_path):
        traits_parser.read(os.path.join(get_abs_path(user, rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return user.subscriptions.get(identifier=traits_parser.get('Common', 'id'))
    else:
        return None 
    

def get_dir(user, rel_path):
    collection = get_collection_of_item(user, rel_path)
    if(collection):
        d = collection.get_dir(rel_path)
        if(d):
            return d
        else:
            return None
    else:
        return None


def get_file(user, rel_path):
    collection = get_collection_of_item(user, rel_path)
    if(collection):
        f = collection.get_file(rel_path)
        if(f):
            return f
        else:
            return None
    else:
        return None


def get_file_size(user, rel_path):
    return os.path.getsize(get_abs_path(user, rel_path))


def get_dir_size(user, rel_path):
    total_size = 0#get_file_size(user, rel_path)
    for item in list_dir(user, rel_path):
        rel_item_path = os.path.join(rel_path, item)
        if is_file(user, rel_item_path):
            total_size += get_file_size(user, rel_item_path)
        elif is_dir(user, rel_item_path):
            total_size += get_dir_size(user, rel_item_path)
    return total_size


def remove_dir_recursive(user, rel_path):
    abs_path = get_abs_path(user, rel_path)
    shutil.rmtree(abs_path)


def get_repository_file_name(file_id, file_name):
    return str(file_id) + "-" + str(file_name) 

def add_file_to_repository(user, rel_src_path, dst_name):
    abs_src_path = get_abs_path(user, rel_src_path)
    shutil.copy(abs_src_path, os.path.join(REPOSITORY_DIR, dst_name))

