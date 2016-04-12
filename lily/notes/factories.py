import random
from datetime import datetime

import pytz
import factory
from factory.declarations import SubFactory, SelfAttribute, LazyAttribute
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.accounts.factories import AccountFactory
from lily.contacts.factories import ContactFactory
from lily.users.factories import LilyUserFactory

from .models import Note


faker = Factory.create('nl_NL')


class NoteFactory(DjangoModelFactory):
    content = LazyAttribute(lambda o: faker.text())
    author = SubFactory(LilyUserFactory, tenant=SelfAttribute('..tenant'))
    sort_by_date = LazyAttribute(lambda o: datetime.now(tz=pytz.utc))

    @factory.lazy_attribute
    def subject(self):
        SubjectFactory = random.choice([AccountFactory, ContactFactory])
        return SubjectFactory(tenant=self.tenant)

    class Meta:
        model = Note
