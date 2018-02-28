from channels.routing import route
from django.conf import settings

from lily.consumers import LilyConsumer, LilyViewConsumer, LilyStaticFilesConsumer

channel_routing = [
    LilyConsumer.as_route(),
]

if settings.DEBUG:
    channel_routing.insert(0, route("http.request", LilyStaticFilesConsumer()))
else:
    channel_routing.insert(0, route("http.request", LilyViewConsumer()))
