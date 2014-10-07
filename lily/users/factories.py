from uuid import uuid4

from django.contrib.auth.models import Group
from factory.declarations import SubFactory, SelfAttribute, LazyAttribute
from factory.django import DjangoModelFactory
from factory.helpers import post_generation

from lily.accounts.factories import AccountFactory
from lily.contacts.factories import ContactWithEmailFactory
from lily.users.models import CustomUser


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    contact = SubFactory(ContactWithEmailFactory, tenant=SelfAttribute('..tenant'))
    account = SubFactory(AccountFactory, tenant=SelfAttribute('..tenant'))
    username = LazyAttribute(lambda o: uuid4().get_hex()[:10])


class AdminCustomUserFactory(CustomUserFactory):
    is_superuser = True
    is_staff = True

    @post_generation
    def groups(self, create, extracted, **kwargs):
        self.password_raw = self.contact.first_name.lower() + '2'
        self.set_password(self.password_raw)
        group = Group.objects.get_or_create(name='account_admin')[0]
        self.groups.add(group)
