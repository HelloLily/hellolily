from email_wrapper_lib.providers.google.parsers import parse_batch_response, parse_folder_list, parse_folder, parse_deletion
from email_wrapper_lib.providers.google.resources.base import GoogleResource


class GoogleFolderResource(GoogleResource):
    def get(self, remote_id):
        folder = {}

        self.batch.add(
            self.service.users().labels().get(
                userId=self.user_id,
                id=remote_id
            ),
            callback=parse_batch_response(parse_folder, folder)
        )

        return folder

    def create(self, name):  # TODO: difference in params with MS.
        folder = {}

        new_folder = {
            'name': name,
            'messageListVisibility': 'show',  # TODO: Default, so remove?
            'labelListVisibility': 'labelShow'  # TODO: Default, so remove?
        }

        self.batch.add(
            self.service.users().labels().create(
                userId=self.user_id,
                body=new_folder
            ),
            callback=parse_batch_response(parse_folder, folder)
        )

        return folder

    def update(self, remote_id, name):
        folder = {}

        update_folder = {
            'id': remote_id,
            'name': name,
        }

        self.batch.add(
            self.service.users().labels().update(
                userId=self.user_id,
                body=update_folder
            ),
            callback=parse_batch_response(parse_folder, folder)
        )

        return folder

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
        folder_resource = GoogleFolderResource(self.service, self.user_id, second_batch)

        self.batch.add(
            self.service.users().labels().list(
                userId=self.user_id,
            ),
            callback=parse_batch_response(parse_folder_list, folders, folder_resource)
        )

        return folders
