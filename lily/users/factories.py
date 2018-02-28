from random import randint

import unicodedata

from django.conf import settings
from django.contrib.auth.hashers import make_password
from factory.declarations import LazyAttribute, SubFactory, Sequence
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from factory.helpers import post_generation
from faker.factory import Factory
from rest_framework.authtoken.models import Token
from timezone_field import TimeZoneField

from lily.tenant.factories import TenantFactory

from .models import Team, LilyUser, UserInfo


faker = Factory.create('nl_NL')


class TeamFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    name = Sequence(lambda n: '%s.%s' % (n, faker.word()))

    class Meta:
        model = Team


class LilyUserFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    password = make_password('admin')

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())
    email = LazyAttribute(lambda o: unicodedata.normalize('NFD', faker.safe_email()).encode('ascii', 'ignore'))
    is_active = LazyAttribute(lambda o: bool(randint(0, 1)))

    phone_number = LazyAttribute(lambda o: faker.phone_number())

    language = FuzzyChoice(dict(settings.LANGUAGES).keys())
    timezone = FuzzyChoice(dict(TimeZoneField.CHOICES).values())

    @post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            if isinstance(extracted, Team):
                # A single team was passed in, use that.
                self.teams.add(extracted)
            else:
                # A list of teams were passed in, use them.
                for team in extracted:
                    self.teams.add(team)

    @post_generation
    def auth_token(self, create, extracted, **kwargs):
        if create:
            Token.objects.create(
                key=self.email.split('@')[0],
                user=self
            )

    @post_generation
    def info(self, create, extracted, **kwargs):
        if create:
            self.info = UserInfo.objects.create()
            self.save()

    class Meta:
        model = LilyUser


class LilySuperUserFactory(LilyUserFactory):
    password = make_password('admin')
    is_superuser = True
    is_staff = True

    @post_generation
    def teams(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            if isinstance(extracted, Team):
                # A single team was passed in, use that.
                self.teams.add(extracted)
            else:
                # A list of teams were passed in, use them.
                for team in extracted:
                    self.teams.add(team)
