from django.conf import settings
from django.core.mail import mail_managers
from django.middleware.common import BrokenLinkEmailsMiddleware
from django.utils.encoding import force_text


class CustomBrokenLinkEmailsMiddleware(BrokenLinkEmailsMiddleware):
    def process_response(self, request, response):
        """
        Send broken link emails for relevant 404 NOT FOUND responses.
        """
        if response.status_code == 404 and not settings.DEBUG:
            domain = request.get_host()
            path = request.get_full_path()
            referer = force_text(request.META.get('HTTP_REFERER', ''), errors='replace')

            if not self.is_ignorable_request(request, path, domain, referer):
                ua = request.META.get('HTTP_USER_AGENT', '<none>')

                # provide the actual ip address, because heroku uses proxies
                if 'HTTP_X_FORWARDED_FOR' in request.META:
                    ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0] or '<none>'
                else:
                    ip = request.META.get('REMOTE_ADDR', '<none>')

                # provide the user
                if request.user.is_authenticated():
                    user = request.user.full_name
                else:
                    user = 'Anonymous user'

                mail_managers(
                    "Broken %slink on %s" % (
                        ('INTERNAL ' if self.is_internal_request(domain, referer) else ''),
                        domain
                    ),
                    "Referrer: %s\n"
                    "Requested URL: %s\n"
                    "Type of request: %s\n"
                    "User agent: %s\n"
                    "IP address: %s\n"
                    "User: %s\n" % (referer, path, request.method, ua, ip, user),
                    fail_silently=True)
        return response
