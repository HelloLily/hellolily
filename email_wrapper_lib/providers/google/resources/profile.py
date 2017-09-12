from email_wrapper_lib.providers.google.parsers import parse_response, parse_profile
from email_wrapper_lib.providers.google.resources.base import GoogleResource


class GoogleProfileResource(GoogleResource):
    def get(self):
        profile = {}

        self.batch.add(
            self.service.users().getProfile(
                userId=self.user_id
            ),
            callback=parse_response(parse_profile, profile)
        )

        return profile
