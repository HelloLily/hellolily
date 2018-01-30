from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_folder, parse_folder_list, parse_deletion
from email_wrapper_lib.providers.microsoft.resources.base import MicrosoftResource


class MicrosoftFolderResource(MicrosoftResource):
    def get(self, remote_id):
        folder = {}

        self.batch.add(
            self.service.get_folder(
                folder_id=remote_id
            ),
            callback=parse_response(parse_folder, folder)
        )

        return folder

    def create(self, remote_id_parent, name):
        folder = {}

        self.batch.add(
            self.service.create_folder(
                folder_id=remote_id_parent,
                name=name
            ),
            callback=parse_response(parse_folder, folder)
        )

        return folder

    def update(self, remote_id, name):
        folder = {}

        self.batch.add(
            self.service.update_folder(
                folder_id=remote_id,
                name=name
            ),
            callback=parse_response(parse_folder, folder)
        )

        return folder

    def delete(self, remote_id):
        status_code = None

        self.batch.add(
            self.service.delete_folder(
                folder_id=remote_id
            ),
            callback=parse_response(parse_deletion, status_code)
        )

        return status_code

    def list(self, folder_id=None, top=50, skip=0):  # TODO: differs from google impl.
        """
        Get a list of folders under the root or the specified folder.

        Paging parameters default to first page.
        """
        folders = {}
        query_parameters = {
            '$top': top,
            '$skip': skip,
        }  # Paging.

        # Successive calls are needed for child folders or next page of folders.
        successive_batch = self.service.new_batch_http_request()
        folder_resource = MicrosoftFolderResource(self.service, self.user_id, successive_batch)

        self.batch.add(
            self.service.get_folders(
                folder_id=folder_id,
                query_parameters=query_parameters
            ),
            callback=parse_response(parse_folder_list, folders, folder_resource)
        )

        return folders
