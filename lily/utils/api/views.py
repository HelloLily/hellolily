import requests

from django.conf import settings
from django.contrib.messages import get_messages
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView


class Queues(APIView):
    """
    List all cases for a tenant.
    """

    def get(self, request, format=None, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.AuthenticationFailed('No permission')

        if not settings.IRONMQ_URL or not settings.IRONMQ_OAUTH:
            raise exceptions.AuthenticationFailed('No permission')

        url = '%s/queues/%s?oauth=%s' % (settings.IRONMQ_URL, kwargs['queue'], settings.IRONMQ_OAUTH)

        resp = requests.get(url)
        queue_info = resp.json()

        if resp.status_code == 200:
            return Response({
                'total_messages': queue_info['total_messages'],
                'size': queue_info['size'],
                'name': queue_info['name'],
            })
        else:
            return exceptions.NotAcceptable

class Notifications(APIView):
    """
    List all notifications posted in request.messages
    """

    def get(self, request, format=None, *args, **kwargs):
        storage = get_messages(request)
        notifications = []

        for message in storage:
            notifications.append({
                'level': message.level_tag,
                'message': message.message,
            })

        return Response(notifications)
