from BeautifulSoup import BeautifulSoup
from django.conf import settings


class PrettifyMiddleware(object):
    """
    HTML code prettification middleware in debug mode for easy debugging.
    """
    def process_response(self, request, response):
        if settings.DEBUG and response['Content-Type'].split(';', 1)[0] == 'text/html':
            response.content = BeautifulSoup(response.content).prettify()
        return response