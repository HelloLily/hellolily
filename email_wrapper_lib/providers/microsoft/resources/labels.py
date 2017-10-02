from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_label, parse_label_list
from email_wrapper_lib.providers.microsoft.resources.base import MicrosoftResource


class MicrosoftLabelsResource(MicrosoftResource):
    def get(self, remote_id):
        label = {}

        self.batch.add(
            self.service.get_folder(
                folder_id=remote_id
            ),
            callback=parse_response(parse_label, label)
        )

        return label

    def list(self, label_id=None, top=50, skip=0):
        """
        Get a list of labels under the root or the specified label.
        Paging parameters default to first page with 50 results.
        """
        labels = {}
        query_parameters = {
            '$top': top,
            '$skip': skip,
        }  # Paging.

        # Successive calls are needed for child labels or next page of labels.
        successive_batch = self.service.new_batch_http_request()
        # TODO: labels_resource because it is also MicrosoftLabelsResource ? (Nitpicking I know)
        label_resource = MicrosoftLabelsResource(self.service, self.user_id, successive_batch)

        self.batch.add(
            self.service.get_folders(
                folder_id=label_id,
                query_parameters=query_parameters
            ),
            callback=parse_response(parse_label_list, labels, label_resource)
        )

        return labels

    def save_create_update(self):
        pass
