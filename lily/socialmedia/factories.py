import random
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from .models import SocialMedia


faker = Factory.create('nl_NL')
twitter_url = 'https://twitter.com/%s'
linkedin_url = 'https://www.linkedin.com/in/%s'


class SocialMediaFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: random.choice(SocialMedia.SOCIAL_NAME_CHOICES)[0])
    username = LazyAttribute(lambda o: faker.user_name())
    profile_url = LazyAttribute(lambda o: random.choice([twitter_url, linkedin_url]) % o.username)

    class Meta:
        model = SocialMedia
