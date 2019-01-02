import httplib2

from googleapiclient.discovery import build


class GmailService(object):
    http = None
    service = None

    def __init__(self, credentials):
        self.http = self.authorize(credentials)
        self.service = self.build_service()

    def authorize(self, credentials):
        return credentials.authorize(httplib2.Http())

    def build_service(self):
        return build('gmail', 'v1', http=self.http)

    def execute_service(self, service):
        return service.execute(http=self._get_http())

    def _get_http(self):
        """
        Return the current http instance. Method added to enable mocking.

        :return: current http instance
        """
        return self.http
