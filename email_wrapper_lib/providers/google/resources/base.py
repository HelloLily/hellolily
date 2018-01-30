class GoogleResource(object):
    def __init__(self, service, user_id, batch):
        self.service = service

        # TODO: check that user_id is not 'me' but an actual user_id.
        self.user_id = user_id

        self.batch = batch
