import logging
import json
import redis
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, **kwargs):
        r = redis.StrictRedis(host=settings.REDIS.hostname, port=settings.REDIS.port, password=settings.REDIS.password)

        # Get the latest commit on the master branch.
        response = requests.get('https://api.github.com/repos/hellolily/hellolily/commits/master')

        data = json.loads(response.text)

        # Store the hash of the commit.
        r.set('app_hash', data['sha'])
