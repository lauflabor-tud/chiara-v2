from chiara.celery import app
from .models import Collection
from authentication.models import User
import sys

from progress.models import ProgressParam, info_progress

import logging
logger = logging.getLogger(__name__)


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

