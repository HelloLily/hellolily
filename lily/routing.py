from channels.routing import route

from lily.consumers import LilyConsumer, LilyViewConsumer, LilyStaticFilesConsumer
from lily.settings import settings

channel_routing = [
    LilyConsumer.as_route(),
]

if settings.DEBUG:
    channel_routing.insert(0, route("http.request", LilyStaticFilesConsumer()))
else:
    channel_routing.insert(0, route("http.request", LilyViewConsumer()))
