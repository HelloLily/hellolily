from email_wrapper_lib.providers.google.parsers.utils import parse_batch_response
from email_wrapper_lib.providers.google.utils import execute_request
from email_wrapper_lib.utils import Promise


class GoogleResource(object):
    def __init__(self, service, user_id):
        self.service = service
        self.user_id = user_id

    def execute(self, request, parser, batch=None):
        if batch:
            promise = Promise()
            batch.add(request, callback=parse_batch_response(parser, promise))

            return promise
        else:
            # No batch object was given so we execute in place.
            data = parser(execute_request(request))

            return data
