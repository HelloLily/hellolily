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
        request = self.service.user().labels().patch(
            userId=self.user_id,
            quotaUser=self.user_id,
            id=remote_id,
            body={
                'name': name,
            }
        )

        return self.execute(request, parse_folder, batch)

    def delete(self, remote_id, batch=None):
        request = self.service.users().labels().delete(
            userId=self.user_id,
            quotaUser=self.user_id,
            id=remote_id
        )

        return self.execute(request, parse_deletion, batch)

    def list(self, batch=None):
        request = self.service.users().labels().list(
            userId=self.user_id,
            quotaUser=self.user_id,
            fields='labels/id',
        )

        return self.execute(request, parse_folder_list, batch)
