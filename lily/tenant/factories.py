from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory
from factory.declarations import SubFactory
from factory.fuzzy import FuzzyChoice
from faker.factory import Factory

from lily.billing.models import Plan, Billing
from lily.utils.countries import COUNTRIES
from lily.utils.models.factories import ExternalAppLinkFactory
from .models import Tenant

faker = Factory.create('nl_NL')


class PlanFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.pystr())
    tier = 2

    class Meta:
        model = Plan


class BillingFactory(DjangoModelFactory):
    subscription_id = LazyAttribute(lambda o: faker.pystr())
    customer_id = LazyAttribute(lambda o: faker.pystr())
    plan = SubFactory(PlanFactory)

    class Meta:
        model = Billing


class TenantFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.company())
    country = FuzzyChoice(dict(COUNTRIES).keys())
    billing = SubFactory(BillingFactory)

    @post_generation
    def external_app_links(self, create, extracted, **kwargs):
        if not create:
            return

        size = extracted.get('size', 1) if extracted else 1
        ExternalAppLinkFactory.create_batch(tenant_id=self.pk, size=size)

    class Meta:
        model = Tenant
