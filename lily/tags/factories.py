from factory.declarations import LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from .models import Tag

faker = Factory.create('nl_NL')


class TagFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.word())

    class Meta:
        model = Tag
