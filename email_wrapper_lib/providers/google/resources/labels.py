from email_wrapper_lib.providers.google.parsers import parse_response, parse_label_list, parse_label
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

    def save_create_update(self):
        pass
