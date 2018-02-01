from email_wrapper_lib.providers.google.parsers.profile import parse_profile
from email_wrapper_lib.providers.google.resources.base import GoogleResource


class ProfileResource(GoogleResource):
    def get(self, batch=None):
        """
        Return the user profile from the api.
        """
        request = self.service.users().getProfile(
            userId=self.user_id,
            quotaUser=self.user_id
        )

        return self.execute(request, parse_profile, batch)
