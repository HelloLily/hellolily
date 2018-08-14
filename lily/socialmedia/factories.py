import random
import unicodedata
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from .models import SocialMedia

faker = Factory.create('nl_NL')
social_media = {
    'twitter': 'https://twitter.com/%s',
    'linkedin': 'https://www.linkedin.com/in/%s',
}


class SocialMediaFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: random.choice(social_media.keys()))  # Only currently supported social media
    username = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.user_name()).encode('ascii', 'ignore'))
    profile_url = LazyAttribute(lambda o: social_media[o.name] % o.username)

    class Meta:
        model = SocialMedia
