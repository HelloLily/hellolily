import random
from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from .models import SocialMedia

faker = Factory.create('nl_NL')


class SocialMediaFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: random.choice(SocialMedia.SOCIAL_NAME_CHOICES)[0])
    username = LazyAttribute(lambda o: faker.user_name())
    profile_url = LazyAttribute(lambda o: faker.uri())

    class Meta:
        model = SocialMedia
