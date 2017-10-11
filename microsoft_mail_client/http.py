"""Classes to encapsulate a single HTTP request.

The classes implement a command pattern, with every object supporting an execute() method that does the actuall HTTP
request.
"""

import json
import uuid
from collections import defaultdict
from urllib import urlencode

import requests
from requests import Response

from microsoft_mail_client import __version__
from microsoft_mail_client.constants import MAX_BATCH_SIZE
from microsoft_mail_client.errors import BatchIdError, BatchMaxSizeError, CallbackError, HttpError


def ddict2dict(dd):
    """
    Convert a defaultdict to a dict. Multiple entries with the same key are merged to one with each value joined
    together by a comma.

    :param dd: defaultdict.
    :return: dict values.
    """
    d = dict()
    for k, v in dd.items():
        if isinstance(v, list):
            d[k] = ",".join(v)
        else:
            d[k] = v
    return d


class HttpRequest(object):
    """Encapsulates a single HTTP request."""

    def __init__(self, uri, method='GET', payload=None, headers=None, parameters=None, request_id=None):
        """
        Constructor for a HttpRequest.
        :param uri: uri to send the request to.
        :param method: http method.
        :param payload: body of the http request.
        :param headers: headers of the http request. defaultdict(list).
        :param parameters: url paramters.
        :param request_id: unique identifier of the request.
        """
        self.uri = uri
        self.method = method
        self.payload = payload
        self.headers = headers or defaultdict(list)  # TODO: change parameter headers=None to headers
        self.parameters = parameters
        self.request_id = request_id or str(uuid.uuid4())

        self.headers.update({
            'User-Agent': 'outlook-api/{0}'.format(__version__),
            'Accept': 'application/json',
            'client-request-id': self.request_id,
            'return-client-request-id': 'true',
        })

        if self.method.upper() in ['PATCH', 'POST']:
            self.headers.update({
                'Content-Type': 'application/json'
            })

        # Request expects a dict, so convert the defaultdict to a dict.
        self.headers = ddict2dict(self.headers)

    def execute(self):
        """
        Execute the request, send to server.

        :return: response object.
        """
        r = None

        if self.method.upper() == 'GET':
            r = requests.get(self.uri, headers=self.headers, params=self.parameters)
        elif self.method.upper() == 'DELETE':
            r = requests.delete(self.uri, headers=self.headers, params=self.parameters)
        elif self.method.upper() == 'PATCH':
            r = requests.patch(self.uri, headers=self.headers, data=json.dumps(self.payload), params=self.parameters)
        elif self.method.upper() == 'POST':
            r = requests.post(self.uri, headers=self.headers, data=json.dumps(self.payload), params=self.parameters)

        return r

    def __repr__(self):
        r = 'Request id:\t{0}\n'.format(self.request_id)
        r += 'Method:\t\t{0}\n'.format(self.method)
        r += 'End point:\t{0}\n'.format(self.uri)
        if self.parameters:
            r += 'Parameters:\n{0}\n'.format(self.parameters)
            r += 'Url:\t\t{0}?{1}\n'.format(self.uri, urlencode(self.parameters))
        r += 'Headers:\n'
        h = self.headers
        for k, v in h.items():
            r += '{0}:{1}\n'.format(k, v)
        if self.payload:
            r += 'Payload:\n{0}\n'.format(json.dumps(self.payload))
        return r


class BatchHttpRequest(object):
    """Batches multiple HttpRequest objects into a single HTTP request."""

    def __init__(self, batch_uri, headers=None, continue_on_error=False):
        """
        Constructor for a BatchHttpRequest.

        :param batch_uri: uri to send the requests to.
        :param headers: defaultdict
        :param continue_on_error: should an error on an individual request halt the complete batch.
        """

        self.uri = batch_uri
        self.batch_id = str(uuid.uuid4())

        # TOOD: use case global callback?
        # self._callback = callback  # Global callback to be called for each individual response in the batch.
        self._requests = []  # List of requests, in the order in which they were added.
        self._callbacks = []  # List of callbacks, in the order in which they were added.
        self._request_ids = []  # List of request ids, in the order in which they were added.
        self._responses = []  # A map from request id to (httplib2.Response, content) response pairs.

        self.headers = headers or defaultdict(list)
        self.headers.update({
            'Content-Type': 'multipart/mixed; boundary=batch_{0}'.format(self.batch_id),
        })

        if continue_on_error:
            self.headers['Prefer'].append('odata.continue-on-error')

        # Request expects a dict, so convert the defaultdict to a dict.
        self.headers = ddict2dict(self.headers)

    @property
    def empty(self):
        return not len(self._requests)

    def add(self, request, callback):
        """
        Add request to the batch queue and adminster the callback to process the response later.

        :param request: HttpRequest object.
        :param callback: callback to process response of added request.
        :return:
        """
        if len(self._requests) == MAX_BATCH_SIZE:
            # TODO: Don't raise this error, just split a too large batch into smaller ones.
            raise BatchMaxSizeError()

        if not callback:
            raise CallbackError()

        if not request.request_id:
            raise BatchIdError('Request without an id added.')

        request_id = request.request_id
        if request_id in self._request_ids:
            raise BatchIdError('Request already added: {0}.'.format(request_id))

        self._requests.append(request)
        self._callbacks.append(callback)
        self._request_ids.append(request_id)

    def execute(self):
        """
        Execute all the requests as a single batched HTTP request.

        First serialize all queued requests to a single request and send it to the server. Finally process the response
        to individual responses and call related callback methods.

        The server may perform operations within a batch in any order.
        :return:
        """
        # TODO: \n or \r\n\r\n ?

        if len(self._request_ids) == 0:
            # No requests to execute.
            return None

        body = self._serialize_requests()

        # Execute batch request.
        batch_response = requests.post(self.uri, data=body, headers=self.headers)

        # TODO?: from google batch http:
        # Loop over all the requests and check for 401s. For each 401 request the credentials should be refreshed and
        # then sent again in a separate batch.

        # TODO: best way to check status_code?
        # if response.status_code >= 300:
        # if batch_response.status_code != requests.codes.ok:
        if not batch_response:
            # raise HttpError()
            batch_response.raise_for_status()

        # A well-formed batch request with correct headers returns HTTP 200 OK. This however doesn't mean all the
        # requests in the batch were successful.

        # Split the batch response body into individual Response objects.
        # Process batch response body by splinting it up and removing none response chunks.
        _, batch_boundary = batch_response.headers['Content-Type'].split('=', 1)
        batch_responses = batch_response.text.strip()  # Remove leading and trailing newlines / white spaces.
        response_chunks = batch_responses.split(batch_boundary)
        # Removes empty chunks and the trailing batch delimiter.
        response_chunks = [chunk for chunk in response_chunks if chunk.strip() and chunk != '--']
        # Each response chunk contains headers, protocol, status, reason & body of individual requests.
        # Process each chunk into a proper Response object
        self._responses = [self._deserialize_response(chunk) for chunk in response_chunks]

        # Process each response by calling the related callback method.
        # Assuming that responses are returned in order the requests were added in the batch.
        # Zip() halts on the shortest list, therefore handling a halting error on a batch component when the
        # odata.continue-on-error header was not provided on the batch request.
        for response, callback, request_id in zip(self._responses, self._callbacks, self._request_ids):
            exception = None
            try:
                if response.status_code >= 300:
                    raise HttpError(response.reason)
            except HttpError as e:
                exception = e

            callback(request_id, response, exception)

    def _serialize_requests(self):
        """
        Convert all the HttpRequest objects in the batch into a single string.

        :return: serialized requests.
        """
        serialized_requests = [self._serialize_request(r) for r in self._requests]
        body = ''
        body += '\n'.join(serialized_requests)
        body += '\n--batch_{0}--\n'.format(self.batch_id)
        body += '\n'

        return body

    def _serialize_request(self, request):
        """
        Convert an HttpRequest object into a string.

        :param request: HttpRequest to serialize.
        :return: string containing the headers, http method and uri with the payload.
        """

        # TODO: \n or \r\n\r\n ?

        body = '\n'  # Make sure you have an additional new line before a batch boundary delimiter.
        body += '--batch_{0}\n'.format(self.batch_id)

        # Override / add headers.
        headers = {}  # request.headers.copy()
        headers.update({
            'Content-Type': 'application/http',
            'Content-Transfer-Encoding': 'binary',
        })

        # Serialize headers.
        for k, v in headers.items():
            body += '{0}:{1}\n'.format(k, v)
        body += '\n'

        # Serialize method & uri.
        uri = request.uri
        if request.parameters:
            uri = '{0}?'.format(uri)
            for k, v in request.parameters.items():
                uri += '{0}={1}&'.format(k, v)
            uri = uri[:-1]  # Remove trailing &-character.

        body += '{0} {1} {2}\n'.format(request.method, uri, 'HTTP/1.1')

        # Serialize payload.
        if request.payload:
            if request.method == 'PATCH' or request.method == 'POST':
                body += '{0}:{1}\n'.format('Content-Type', 'application/json')

            body += '\n'
            body += json.dumps(request.payload)
            body += '\n'

        return body

    def _deserialize_response(self, chunk):
        """
        Convert a string into a Response object.

        Chunk consists of headers, protocol, status, reason & optional a body.
        :param chunk: string representation of a response.
        :return: Response object.
        """
        headers = {}
        body = ''

        lines = chunk.splitlines()
        lines = [line for line in lines if line.strip() and line != '--']

        # One line can be a header, or list the protocol, status & reason or be part of the body.
        # Indentify a header by :-character or
        # it starts with the protocol (HTTP) or
        # otherwise, it is part of the response body.
        while lines:
            line = lines.pop(0)
            if line.startswith('{'):
                # Start of the (json) body.
                # TODO: return remainig lines, now it assumes remaining is also the last line.
                # lines = lines.insert(0, line)
                body = line
                break
            elif ':' in line:
                key, value = [x.strip() for x in line.split(':', 1)]
                headers.update({
                    key: value,
                })
            elif line.startswith('HTTP'):
                protocol, status, reason = line.split(' ', 2)
        #
        # if lines:
        #     # The remainder of lines contains the body of the response.
        #     body = '\n'.join(lines)
        #

        response = Response()
        response.status_code = int(status)
        response.reason = reason
        if headers:
            response.headers = headers
        if body:
            # TODO: proper way of encoding?
            response._content = bytes(body)
            # response._content = bytes(body, 'unicode')
            # response._content = body.encode('unicode')  # Response object expects unicode bytes. <- fails

        return response

    def __repr__(self):
        r = 'Batch id:\t{0}\n'.format(self.batch_id)
        r += 'Method:\t\t{0}\n'.format("POST")
        r += 'Url:\t\t{0}\n'.format(self.uri)
        r += 'Headers:\n'
        h = self.headers
        for k, v in h.items():
            r += '{0}:{1}\n'.format(k, v)
        if self._request_ids:
            r += 'Payload:\n{0}\n'.format(self._serialize_requests())
        return r
