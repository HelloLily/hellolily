import json

import newrelic.agent
from channels import Group
from channels.generic.websockets import WebsocketConsumer
from channels.handler import ViewConsumer
from channels.staticfiles import StaticFilesConsumer


class LilyConsumer(WebsocketConsumer):
    http_user = True

    def connect(self, message, **kwargs):
        if message.user.is_anonymous:
            message.reply_channel.send({
                "text": json.dumps({
                    'error': 'unauthenticated',
                }),
                "close": True,
            })
        else:
            message.reply_channel.send({"accept": True})
            # Subscribe to user group
            Group("user-%s" % message.user.id).add(message.reply_channel)
            # Subscribe to tenant group
            Group("tenant-%s" % message.user.tenant_id).add(message.reply_channel)
            # Subscribe to team groups
            for team in message.user.teams.all():
                Group("team-%s" % team.id).add(message.reply_channel)

    def disconnect(self, message, **kwargs):
        if not message.user.is_anonymous:
            # Remove user from all groups it was added to
            Group("user-%s" % message.user.id).discard(message.reply_channel)
            Group("tenant-%s" % message.user.tenant_id).discard(message.reply_channel)
            for team in message.user.teams.all():
                Group("team-%s" % team.id).discard(message.reply_channel)


class LilyViewConsumer(ViewConsumer):
    @newrelic.agent.background_task()
    def __call__(self, message):
        return super(LilyViewConsumer, self).__call__(message)


class LilyStaticFilesConsumer(StaticFilesConsumer):
    @newrelic.agent.background_task()
    def __call__(self, message):
        return super(LilyStaticFilesConsumer, self).__call__(message)
