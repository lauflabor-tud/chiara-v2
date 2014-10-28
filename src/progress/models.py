from omnibus.api import publish
import time


class Progress():
    def __init__(self, task_id, collection, rel_path):
        self.task_id = task_id
        self.collection = collection
        self.rel_path = rel_path


class ProgressParam():
    TOTAL = 'total'
    CURRENT = 'current'
    CURRENT_POS = 'current_pos'
    MESSAGE = 'message'
    

def start_progress(task_id, data):
    data[ProgressParam.CURRENT] = 0
    data[ProgressParam.CURRENT_POS] = ''
    for _ in range(1, 5):
        update_progress(task_id, data)
        time.sleep(0.2);
    

def update_progress(task_id, data):
    channel = 'progress' + task_id
    event = 'update'
    
    current = data.get(ProgressParam.CURRENT)
    total = data.get(ProgressParam.TOTAL)
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
    
    
    
    