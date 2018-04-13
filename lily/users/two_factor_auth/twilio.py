from django.conf import settings
from two_factor.gateways.twilio.gateway import Twilio


class LilyTwilioGateway(Twilio):
    """
    Override the Twilio gateway to send a custom body.
    """

    def send_sms(self, device, token):
        body = 'Your Lily token is: %s' % token
        self.client.messages.create(
            to=device.number.as_e164,
            from_=getattr(settings, 'TWILIO_CALLER_ID'),
            body=body
        )
