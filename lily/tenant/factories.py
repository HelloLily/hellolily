from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory
from faker.factory import Factory

from lily.utils.models.factories import ExternalAppLinkFactory
from .models import Tenant

faker = Factory.create('nl_NL')


class TenantFactory(DjangoModelFactory):
    name = LazyAttribute(lambda o: faker.company())

    @post_generation
    def external_app_links(self, create, extracted, **kwargs):
        if not create:
            return

        size = extracted.get('size', 1) if extracted else 1
        ExternalAppLinkFactory.create_batch(tenant_id=self.pk, size=size)

    class Meta:
        model = Tenant
