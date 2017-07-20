from email_wrapper_lib.providers.google.resources.base import GoogleResource


class GoogleProfileResource(GoogleResource):
    def get(self):
        profile = self.service.users().getProfile(userId='me').execute()

        return {
            'user_id': profile['emailAddress'],
            'username': profile['emailAddress']
        }
