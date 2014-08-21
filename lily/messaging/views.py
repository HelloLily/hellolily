# # Django imports
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView

# # Lily imports
# from lily.messaging.models import Message, MessagesAccount


class DashboardView(ListView):
    """
    Dashboard of messages, display inbox and other cool stuff.
    """
#     template_name = 'messaging/dashboard.html'


#     def get_queryset(self):
#         account_list = MessagesAccount.objects.filter(user_group=self.request.user)

#         # pass the account list to a task which will look for new messages
#         for account in account_list:
#             result = account.sync(blocking=True)
# #            print result

#         message_list = Message.objects.filter(account__in=account_list).order_by('-datetime')[:20]

#         return message_list


# Perform logic here instead of in urls.py
dashboard_view = login_required(DashboardView.as_view())
