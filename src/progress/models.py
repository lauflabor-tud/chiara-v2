from omnibus.api import publish
import time


class Progress():
    def __init__(self, task_id, collection, rel_path):
        self.task_id = task_id
        self.collection = collection
        self.rel_path = rel_path
    

def start_progress(task_id, data):
    for _ in range(1, 5):
        update_progress(task_id, data)
        time.sleep(0.2);
    


def update_progress(task_id, data):
    channel = 'progress' + task_id
    event = 'update'
    
    current = data.get('current')
    total = data.get('total')
    progress = ((current*10000)/total) / 100.0

    publish(
        channel,
        event,
        {'current' : current,
         'total' : total,
         'progress' : progress,
         'finish' : data.get('finish'),
         'error' : data.get('error'),
         'message' : data.get('message')},
        sender='server'
    )
    time.sleep(1)