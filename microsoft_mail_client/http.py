"""Classes to encapsulate a single HTTP request.

The classes implement a command pattern, with every object supporting an execute() method that does the actuall HTTP
request.
"""

import json
import pprint
import uuid

import requests
from requests import Response

from microsoft_mail_client import __version__
from microsoft_mail_client.constants import MAX_BATCH_SIZE
from microsoft_mail_client.errors import BatchIdError, BatchMaxSizeError, CallbackError


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
        self.headers = headers or {}  # TODO: change headers=None to headers
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

    def execute(self):
        """
        Execute the request, send to server.

        :return: response object.
        """
        response = None

        # Request expects a dict, so convert the defaultdict to a dict.
        headers = self._ddict2dict(self.headers)

        pprint.pprint(json.dumps(self.uri), width=1)
        pprint.pprint(json.dumps(self.method), width=1)
        if self.payload:
            pprint.pprint(self.payload, width=1)
        pprint.pprint(headers, width=1)
        if self.parameters:
            pprint.pprint(self.parameters, width=1)

        if self.method.upper() == 'GET':
            response = requests.get(self.uri, headers=headers, params=self.parameters)
        elif self.method.upper() == 'DELETE':
            response = requests.delete(self.uri, headers=headers, params=self.parameters)
        elif self.method.upper() == 'PATCH':
            response = requests.patch(self.uri, headers=headers, data=json.dumps(self.payload), params=self.parameters)
        elif self.method.upper() == 'POST':
            response = requests.post(self.uri, headers=headers, data=json.dumps(self.payload), params=self.parameters)

        return response

    def _ddict2dict(self, dd):
        """
        Convert a defaultdict to a dict. List values are joined together by a comma.

        :param dd: defaultdict.
        :return: dict values.
        """
        headers = {}
        for k, v in dd.items():
            if isinstance(v, list):
                headers[k] = ",".join(v)
            else:
                headers[k] = v
        return headers


class BatchHttpRequest(object):
    """Batches multiple HttpRequest objects into a single HTTP request."""

    def __init__(self, batch_uri, headers):
        """
        Constructor for a BatchHttpRequest.

        :param batch_uri: uri to send the requests to.
        :param headers:
        """

        self.uri = batch_uri
        self.batch_id = str(uuid.uuid4())

        # TOOD: use case global callback?
        # self._callback = callback  # Global callback to be called for each individual response in the batch.
        self._requests = {}  # A map from id to request.
        self._callbacks = {}  # A map from id to callback.
        # self._responses = {}  # A map from request id to (httplib2.Response, content) response pairs.

        self.headers = headers or {}
        self.headers.update({
            'Content-Type': 'multipart/mixed; boundary=batch_'.format(self.batch_id),
        })

    def add(self, request, callback):
        """
        Add request to the batch queue and adminster the callback to process the response later.

        :param request: HttpRequest object.
        :param callback: callback to process response of added request.
        :return:
        """
        if len(self._requests) == MAX_BATCH_SIZE:
            raise BatchMaxSizeError()

        if not callback:
            raise CallbackError()

        if not request.request_id:
            raise BatchIdError('Request without an id added.')

        request_id = request.request_id

        if request_id in self._requests:
            raise BatchIdError('Request already added: {0}.'.format(request_id))

        self._requests[request_id] = request
        self._callbacks[request_id] = callback

    def execute(self, continue_on_error=False):
        """
        Execute all the requests as a single batched HTTP request.

        First serialize all queued requests to a single request and send it to the server. Finally process the response
        to individual responses and call related callback methods.

        The server may perform operations within a batch in any order.
        :param continue_on_error: should an error on an individual request halt the complete batch.
        :return:
        """
        # TODO: \n or \r\n\r\n ?

        if len(self._requests) == 0:
            # No requests to execute.
            return None

        if continue_on_error:
            self.headers.update({
                'Prefer': 'odata.continue-on-error'
            })

        body = ''

        # Serialize requests.
        serialized_requests = [self._serialize_request(r) for r in self._requests.values()]
        body += '\n'.join(serialized_requests)
        body += '\n'
        body += '--batch_{0}--\n'.format(self.batch_id)

        if self._requests.values()[-1].method == 'POST':
            # if you have a POST request at the end of a batch, make sure there is a new line after the very last batch
            # delimiter.
            body += '\n'

        # Execute batch request.
        batch_response = requests.post(self.uri, data=body, headers=self.headers)

        # TODO?: from google batch http:
        # Loop over all the requests and check for 401s. For each 401 request the credentials should be refreshed and
        # then sent again in a separate batch.

        # if response.status >= 300:
        # if batch_response.status_code != requests.codes.ok:
        if not batch_response:
            # raise HttpError()
            batch_response.raise_for_status()

        # Split the batch response body into individual Response objects.
        # Process batch response body by splinting it up and removing none response chunks.
        batch_responses = batch_response.text.strip()  # Remove leading and trailing newlines / white spaces.
        delimiter = '--batchresponse_{0}'.format(self.batch_id)
        response_chunks = batch_responses.split(delimiter)
        # Removes empty chunks and the trailing batch delimiter.
        response_chunks = [chunk for chunk in response_chunks if chunk.strip() and chunk != '--']
        # Each response chunk contains headers, protocol, status, reason & body of individual requests.
        # Process each chunk into a proper Response object
        responses = [self._deserialize_response(chunk) for chunk in response_chunks]

        # Process each response by calling the related callback method,
        for response in responses:
            # Extract client-request-id from the response headers.
            # TODO: client-request-id not available possibillity?
            request_id = response.headers['client-request-id']
            # Retrieve the specific callback for this request,
            callback = self._callbacks[request_id]
            # and process the response.
            callback(response)

    def _serialize_request(self, request):
        """
        Convert an HttpRequest object into a string.

        :param request: HttpRequest to serialize.
        :return: string containing the headers, http method and uri with the payload.
        """

        # TODO: \n or \r\n\r\n ?

        body = '\n\n'  # Make sure you have an additional new line before a batch boundary delimiter.
        body += '--batch_{0}\n'.format(self.batch_id)

        # Override / add headers.
        headers = request.headers.copy()
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
        body += '\n'

        # Serialize payload.
        if request.payload:
            if request.method == 'PATCH' or request.method == 'POST':
                body += '{0}:{1}\n'.format('Content-Type', 'application/json')

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

        lines = chunk.splitlines(keepends=False)
        # One line can be a header, or list the protocol, status & reason or be part of the body.
        # Indentify a header by :-character or
        # it starts with the protocol (HTTP) or
        # otherwise, it is part of the response body.
        while lines:
            if lines[0].startswith('HTTP'):
                line = lines.pop(0)
                protocol, status, reason = line.split(' ', 2)
            elif ';' in lines[0]:
                line = lines.pop(0)
                key, value = [x.strip() for x in line.split(':', 1)]
                headers.update({
                    key: value,
                })
            elif lines[0].startswith('{'):
                # Start of the (json) body.
                break

        if lines:
            # The remainder of lines contains the body of the response.
            body = '\n'.join(lines)

        response = Response()
        response.status_code = status
        response.reason = reason
        if headers:
            response.headers = headers
        if body:
            # TODO: proper way of encoding?
            # response._content = bytes(body)
            # response._content = bytes(body, 'unicode')
            response._content = body.encode('unicode')  # Response object expects unicode bytes.

        return response
