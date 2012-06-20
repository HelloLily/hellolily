import importlib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from lily.messages.models import Message


CONNECTORS = []
for app in settings.MESSAGE_APPS:
    module = importlib.import_module('%s.connector' % app)
    CONNECTORS.append(module.Connector)


class DashboardView(TemplateView):
    template_name = 'messages/dashboard.html'


class MessageListView(ListView):
    """
    Dashboard of messages, display inbox and other cool stuff.

    """
    template_name = 'messages/message_list.html'

    messages = Message.objects.all()
    print messages
    
    def get_queryset(self):
        complete_message_list = []

        for conn in CONNECTORS:
            host = 'imap.gmail.com'
            user = 'lily@hellolily.com'
            password = '0$mxsq=3ouhr)_iz710dj!*2$vkz'
            message_list = conn(host=host, port=993, user=user, password=password).get_message_list(limit=10)
            complete_message_list += message_list

        complete_message_list.sort(key=lambda item:item['date'], reverse=True)

        return complete_message_list


# Perform logic here instead of in urls.py
dashboard_view = login_required(DashboardView.as_view())
message_list_view = login_required(MessageListView.as_view())