from django.http.response import StreamingHttpResponse
from django.template.response import TemplateResponse
from chiara.settings.common import OMNIBUS_ENDPOINT_SCHEME, OMNIBUS_SERVER_HOST, OMNIBUS_SERVER_PORT


def update_progress(request, action, task_id):
    t = TemplateResponse(request, 'progress/progress.html',
                         {'action' : action,
                          'task_id': task_id,
                          'omnibus_endpoint': OMNIBUS_ENDPOINT_SCHEME + ':\/\/' + OMNIBUS_SERVER_HOST + ':' + OMNIBUS_SERVER_PORT + '\/ec'})
    return StreamingHttpResponse(t.render())




