import logging
import sys

from authentication.models import User
from chiara.celery import app
from exception.exceptions import MissingDescriptionFileException, \
    NoLocalChangesException, NotNewestRevisionException
from progress.models import ProgressParam, info_progress, error_progress

from .models import Collection


logger = logging.getLogger(__name__)


@app.task(bind=True)  
def add_to_collection(self, user_id, rel_path, message=None):
    try:
        user = User.objects.get(id=user_id)
        collection = Collection()
        collection.add_to_collection(user, rel_path, self.request.id)
    
        # info progress
        if message is None:
            message = "You have successfully add the directory '" + rel_path + "' to the repository!"
        data = {ProgressParam.MESSAGE : message}
        info_progress(self.request.id, data)
    except MissingDescriptionFileException:
        message = "No description file found!"
        data = {ProgressParam.MESSAGE : message}
        error_progress(self.request.id, data)


@app.task(bind=True) 
def push_local_revision(self, user_id, rel_path, col_id, col_rev, comment, message=None):
    try:
        user = User.objects.get(id=user_id)
        prev_col = Collection.objects.get(identifier=col_id, revision=col_rev)
        collection = Collection()
        collection.push_local_revision(user, rel_path, prev_col, comment, self.request.id)
        
        # info progress
        if message is None:
            message = "You have successfully pushed the local revision of '" + collection.directory.name + "' to the repository!"
        data = {ProgressParam.MESSAGE : message}
        info_progress(self.request.id, data)
    except NoLocalChangesException: 
        message = "There are no local changes of this collection in your webfolder!"
        data = {ProgressParam.MESSAGE : message}
        error_progress(self.request.id, data)
    except NotNewestRevisionException:
        message = "You have to update to the newest revision of this collection before pushing a new one!"
        data = {ProgressParam.MESSAGE : message}
        error_progress(self.request.id, data)


@app.task(bind=True)  
def download(self, user_id, rel_path, col_id, col_rev=None, message=None):
    user = User.objects.get(id=user_id)
    if col_rev is None:
        collection = Collection.objects.get(identifier=col_id, revision=1)
        collection = collection.get_revision(sys.maxint)
    else:
        collection = Collection.objects.get(identifier=col_id, revision=col_rev)
    
    collection.download(user, rel_path, self.request.id)
    
    # info progress
    if message is None:
        message = "You have successfully downloaded the collection '"  + collection.name + "' into the directory '" + rel_path + "'!"    
    data = {ProgressParam.MESSAGE : message}
    info_progress(self.request.id, data)
    
    return 'done'


@app.task(bind=True)  
def download_public(self, rel_path, col_id, col_rev=None, message=None):
    if col_rev is None:
        collection = Collection.objects.get(identifier=col_id, revision=1)
        collection = collection.get_revision(sys.maxint)
    else:
        collection = Collection.objects.get(identifier=col_id, revision=col_rev)
    
    collection.download_public(rel_path, self.request.id)
        
    # info progress
    if message is None:
        message = "You have successfully downloaded the collection '"  + collection.name + "' into the directory '" + rel_path + "'!"    
    data = {ProgressParam.MESSAGE : message}
    info_progress(self.request.id, data)
    
    return 'done'

