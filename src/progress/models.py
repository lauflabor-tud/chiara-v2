from celery import current_app
from celery.result import AsyncResult
from omnibus.api import publish
import time

import logging
logger = logging.getLogger(__name__)


def start_progress(task_id, data):
    # set current state to zero
    data[ProgressParam.CURRENT] = 0
    data[ProgressParam.CURRENT_POS] = ''
    # update progress
    for _ in range(1, 5):
        update_progress(task_id, data)
        time.sleep(0.2);
    

def update_progress(task_id, data):
    channel = 'progress' + task_id
    event = 'update'
    
    current = data.get(ProgressParam.CURRENT)
    total = data.get(ProgressParam.TOTAL)
    if total==0:
        progress = 0
    else:
        progress = ((current*10000)/total) / 100.0
        
    publish(
        channel,
        event,
        {ProgressParam.CURRENT : current,
         ProgressParam.TOTAL : total,
         'progress' : progress,
         ProgressParam.CURRENT_POS : data.get(ProgressParam.CURRENT_POS)
        },
        sender='server'
    )
    time.sleep(1)
    
    
def info_progress(task_id, data):
    channel = 'progress' + task_id
    event = 'info'
    
    publish(
        channel,
        event,
        {ProgressParam.MESSAGE : data.get(ProgressParam.MESSAGE)},
        sender='server'
    )
    
    
def error_progress(task_id, data):
    channel = 'progress' + task_id
    event = 'error'
    
    publish(
        channel,
        event,
        {ProgressParam.MESSAGE : data.get(ProgressParam.MESSAGE)},
        sender='server'
    )



class ProgressParam():
    REL_PATH = "rel_path"
    
    TOTAL = 'total'
    CURRENT = 'current'
    CURRENT_POS = 'current_pos'
    MESSAGE = 'message'
    

class ProgressBackend(object):
    
    _BACKEND = None
    
    progress_state = 'PROGRESS'

    @classmethod
    def get_backend(cls):
        if cls._BACKEND is None:
            cls._BACKEND = ProgressBackend()
        return cls._BACKEND
    

    def __init__(self):
        self.app = current_app

    def set_data(self, task_id, data):
        self.app.backend.store_result(task_id, data, self.progress_state)
    
    def update_data(self, task_id, data):
        updated_data = self.get_data(task_id)
        for k,v in data.iteritems():
            print k, v
            updated_data[k] = v
        self.app.backend.store_result(task_id, updated_data, self.progress_state)
    
    def get_data(self, task_id):
        return AsyncResult(task_id).info
    
