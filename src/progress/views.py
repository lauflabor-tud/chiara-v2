from django.http.response import StreamingHttpResponse
from django.template.response import TemplateResponse


def update_progress(request, action, task_id):
    t = TemplateResponse(request, 'progress/progress.html',
                         {'action' : action,
                          'task_id': task_id})
    return StreamingHttpResponse(t.render())