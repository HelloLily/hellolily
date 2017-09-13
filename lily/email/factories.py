from factory import post_generation
from factory.declarations import SubFactory, LazyAttribute, Iterator, SelfAttribute
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from email_wrapper_lib.models.models import EmailAccount
from lily.email.models import EmailAccountConfig
from lily.tenant.factories import TenantFactory
from lily.users.models import Team, LilyUser


faker = Factory.create('nl_NL')


class EmailAccountConfigFactory(DjangoModelFactory):
    tenant = SubFactory(TenantFactory)
    email_account = Iterator(EmailAccount.objects.all())

    from_name = LazyAttribute(lambda o: faker.name())
    label = SelfAttribute('.email_account.username')

    privacy = FuzzyChoice(range(3))
    shared_with_everyone = FuzzyChoice([True, False])

    @post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, use them.
            for user in extracted:
                self.owners.add(user)
        else:
            # Pick a user from the database and assign it as owner.
            user = LilyUser.objects.filter(tenant=self.tenant).order_by('?').first()
            self.owners.add(user)

    @post_generation
    def shared_with_users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, use them.
            for user in extracted:
                self.shared_with_users.add(user)
        else:
            # Pick a user from the database and assign it as owner.
            user = LilyUser.objects.filter(tenant=self.tenant).order_by('?').first()
            self.shared_with_users.add(user)

    @post_generation
    def shared_with_teams(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, use them.
            for team in extracted:
                self.shared_with_teams.add(team)
        else:
            # Pick a user from the database and assign it as owner.
            team = Team.objects.filter(tenant=self.tenant).order_by('?').first()
            self.shared_with_teams.add(team)

    class Meta:
        model = EmailAccountConfig
