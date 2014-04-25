import os, math, ConfigParser
from chiara.settings.common import WEBDAV_DIR, COLLECTION_INFO_DIR, COLLECTION_SUBSCRIPTION_FILE, COLLECTION_TRAITS_FILE
import utils.path

config = ConfigParser.RawConfigParser()

import logging
logger = logging.getLogger("utils")

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
    if(os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_SUBSCRIPTION_FILE)) and
       os.path.exists(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))):
        config.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return bool(user.subscriptions.filter(identifier=config.get('Common', 'id')))
    else:
        return False
    

def get_collection_of_item(user, rel_path):
    rel_path = utils.path.no_slash(rel_path)
    abs_path = get_abs_path(user, rel_path)
    if (rel_path=="" or not os.path.exists(abs_path)):
        return None
    elif is_collection(user, rel_path):
        config.read(os.path.join(abs_path, COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return user.subscriptions.get(identifier=config.get('Common', 'id'))
    else:
        return get_collection_of_item(user, os.path.split(rel_path)[0])


def get_collection(user, rel_path):
    if is_collection(user, rel_path):
        config.read(os.path.join(get_abs_path(user, rel_path), COLLECTION_INFO_DIR, COLLECTION_TRAITS_FILE))
        return user.subscriptions.get(identifier=config.get('Common', 'id'))
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


def convert_size(size):
    if size >= math.pow(10,12):
        return str(round(size / math.pow(10,12), 2)) + " TB";
    elif size >= math.pow(10,9):
        return str(round(size / math.pow(10,9), 2)) + " GB";
    elif size >= math.pow(10,6):
        return str(round(size / math.pow(10,6), 2)) + " MB";
    elif size >= math.pow(10,3):
        return str(round(size / math.pow(10,3), 2)) + " KB";
    else:
        return str(size) + " B";

