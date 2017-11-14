from email_wrapper_lib.providers.google.parsers import parse_response, parse_label_list, parse_label, parse_deletion
from email_wrapper_lib.providers.google.resources.base import GoogleResource


class GoogleLabelsResource(GoogleResource):
    def get(self, remote_id):
        label = {}

        self.batch.add(
            self.service.users().labels().get(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_response(parse_label, label)
        )

        return label

    def create(self, name):  # TODO: difference in params with MS.
        label = {}

        new_label = {
            'name': name,
            'messageListVisibility': 'show',  # TODO: Default, so remove?
            'labelListVisibility': 'labelShow'  # TODO: Default, so remove?
        }

        self.batch.add(
            self.service.users().labels().create(
                userId=self.user_id,
                body=new_label
            ),
            callback=parse_response(parse_label, label)
        )

        return label

    def update(self, remote_id, name):
        label = {}

        update_label = {
            'id': remote_id,
            'name': name,
        }

        self.batch.add(
            self.service.users().labels().update(
                userId=self.user_id,
                body=update_label
            ),
            callback=parse_response(parse_label, label)
        )

        return label

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.users().labels().delete(
                userId=self.user_id,
                id=remote_id),
            callback=parse_response(parse_deletion, status_code)
        )

        return status_code

    def list(self):
        labels = {}

        # Because Google only gives message ids, we need to do a second batch for the bodies.
        second_batch = self.service.new_batch_http_request()
        # TODO: labels_resource because it is also GoogleLabelsResource ? (Nitpicking I know)
        label_resource = GoogleLabelsResource(self.service, self.user_id, second_batch)

        self.batch.add(
            self.service.users().labels().list(
                userId=self.user_id,
            ),
            callback=parse_response(parse_label_list, labels, label_resource)
        )

        return labels
