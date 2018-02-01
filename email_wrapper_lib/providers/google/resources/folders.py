from email_wrapper_lib.providers.google.parsers.folders import parse_folder_list, parse_folder
from email_wrapper_lib.providers.google.parsers.utils import parse_batch_response, parse_deletion
from email_wrapper_lib.providers.google.resources.base import GoogleResource


class FoldersResource(GoogleResource):
    def get(self, folder_id, batch=None):
        """
        Return a single folder from the api.
        """
        request = self.service.users().labels().get(
            userId=self.user_id,
            quotaUser=self.user_id,
            id=folder_id
        )

        return self.execute(request, parse_folder, batch)

    def create(self, name, batch=None):
        request = self.service.user().labels().create(
            userId=self.user_id,
            quotaUser=self.user_id,
            body={
                'name': name,
                'messageListVisibility': 'show',
                'labelListVisibility': 'labelShow',
                'type': 'user',
            }
        )

        return self.execute(request, parse_folder, batch)

    def update(self, remote_id, name, batch=None):
        request = self.service.user().labels().update(
            userId=self.user_id,
            quotaUser=self.user_id,
            id=remote_id,
            body={
                'id': remote_id,
                'name': name,
                'messageListVisibility': 'show',
                'labelListVisibility': 'labelShow',
            }
        )

        return self.execute(request, parse_folder, batch)

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.users().labels().delete(
                userId=self.user_id,
                id=remote_id),
            callback=parse_batch_response(parse_deletion, status_code)
        )

        return status_code

    def list(self):
        folders = {}

        # Because Google only gives message ids, we need to do a second batch for the bodies.
        second_batch = self.service.new_batch_http_request()
        folder_resource = GoogleFolderResource(self.service, self.user_id)

        self.batch.add(
            self.service.users().labels().list(
                userId=self.user_id,
            ),
            callback=parse_batch_response(parse_folder_list, folders)
        )

        return folders
