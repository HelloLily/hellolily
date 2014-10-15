import json
import re

from celery.result import AsyncResult, TimeoutError
from django.http import HttpResponse
from django.views.generic.base import View

from taskmonitor.models import TaskStatus
from lily.utils.views.mixins import LoginRequiredMixin


class TaskStatusView(LoginRequiredMixin, View):
    """
    Checks if a task is finished and returns result if it's available.
    """
    http_method_names = ['get']
    model = TaskStatus

    def get(self, request, *args, **kwargs):
        task_id = kwargs.pop('task_id')
        async_result = AsyncResult(task_id)

        task_status = TaskStatus.objects.get(task_id=task_id)

        # Strip parentheses and get the name of the function to call
        task_name = re.sub(r'\([^)]*\)', '', task_status.signature)

        try:
            # Poll the task to see if the result is available
            result = async_result.get(timeout=20)
        except TimeoutError:
            result = None

        if task_name in request.session['tasks']:
            del(request.session['tasks'][task_name])
            request.session.modified = True

        # Setup the response
        response = {'task_id': task_id, 'task_status': task_status.status, 'task_name': task_name, 'task_result': result}

        return HttpResponse(json.dumps(response), content_type='application/json')
