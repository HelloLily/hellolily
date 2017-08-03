"""Classes to encapsulate a single HTTP request.

The classes implement a command pattern, with every object supporting an execute() method that does the actuall HTTP
request.
"""

import json
import uuid

import requests

from microsoft_mail_client import __version__


class HttpRequest(object):
    """Encapsulates a single HTTP request."""

    def __init__(self, uri, method='GET', payload=None, headers=None, parameters=None, request_id=None):
        self.uri = uri
        self.method = method
        self.payload = payload
        self.headers = headers
        self.parameters = parameters
        self.request_id = request_id or str(uuid.uuid4())

    def execute(self):
        self.headers.update({
            'User-Agent': 'outlook-api/{0)'.format(__version__),
            'Accept': 'application/json',
        })

        self.headers.update({
            'client-request-id': self.request_id,
            'return-client-request-id': 'true',
        })

        response = None

        if self.method.upper() == 'GET':
            response = requests.get(self.uri, headers=self.headers, params=self.parameters)
        elif self.method.upper() == 'DELETE':
            response = requests.delete(self.uri, headers=self.headers, params=self.parameters)
        elif self.method.upper() == 'PATCH':
            self.headers.update({
                'Content-Type': 'application/json'
            })
            response = requests.patch(self.uri, headers=self.headers, data=json.dumps(self.payload),
                                      params=self.parameters)
        elif self.method.upper() == 'POST':
            self.headers.update({
                'Content-Type': 'application/json'
            })
            response = requests.post(self.uri, headers=self.headers, data=json.dumps(self.payload),
                                     params=self.parameters)

        return response


class BatchHttpRequest(object):
    """Batches multiple HttpRequest objects into a single HTTP request."""

    def __init__(self, callback=None, batch_uri):
        """Constructor for a BatchHttpRequest."""
        self._batch_uri = batch_uri

    def execute(self, http, order, requests):
        """Execute all the requests as a single batched HTTP request."""
        pass

    def add(self, request, callback=None, request_id=None):
        pass
