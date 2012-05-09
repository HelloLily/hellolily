import importlib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView


class DashboardView(ListView):
    """
    Dashboard of messages, display inbox and other cool stuff.
    """
    template_name = 'messages/dashboard.html'
    
    def get_queryset(self):
        apps = settings.MESSAGE_APPS
        complete_message_list = []
        for app in apps:
            module = importlib.import_module('%s.commands' % app)
            message_list = module.get_message_list()
            
            complete_message_list += message_list
        
        # for every app in the message_app list we need to call the get_messages function
        # append the results from that function call to object list
        # sort the object list
        # return the sorted object list
        
        complete_message_list.sort(key=lambda item:item['date'], reverse=True)
                
        return complete_message_list


# Perform logic here instead of in urls.py
dashboard_view = login_required(DashboardView.as_view())