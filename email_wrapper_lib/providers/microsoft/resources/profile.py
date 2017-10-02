from email_wrapper_lib.providers.microsoft.parsers import parse_response, parse_profile
from email_wrapper_lib.providers.microsoft.resources.base import MicrosoftResource


class MicrosoftProfileResource(MicrosoftResource):
    def get(self):
        profile = {}
        # TODO: Only request usefull data?
        # query_parameters = {'$select': 'DisplayName,EmailAddress'}

        self.batch.add(
            self.service.get_me(),
            callback=parse_response(parse_profile, profile)
        )

        return profile
