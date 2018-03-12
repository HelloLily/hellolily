from email_wrapper_lib.providers.google.parsers.utils import parse_batch_response, handle_exception
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
            try:
                data = request.execute()

                return parser(data)
            except Exception as exception:
                handle_exception(exception)


