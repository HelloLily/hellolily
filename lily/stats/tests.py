from django.core.urlresolvers import reverse
from django.test import TestCase

from lily.users.factories import LilyGroupFactory, LilyUserFactory
from .urls import case_patterns, deal_patterns


class StatsTests(TestCase):
    def test_no_errors(self):
        """
        Test that the stats pages give no errors.
        """
        user_obj = LilyUserFactory(is_active=True)
        lilygroup = LilyGroupFactory()
        self.client.login(email=user_obj.email, password='admin')

        for pattern in case_patterns:
            # Loop over case patterns, these need the lilygroup_id kwarg.
            response = self.client.get(reverse(pattern.name, kwargs={
                'lilygroup_id': lilygroup.id,
            }))

            if response.status_code != 200:
                import ipdb
                ipdb.set_trace()

            self.assertEqual(response.status_code, 200)

        for pattern in deal_patterns:
            # Loop over deal patterns, these need no kwargs.
            response = self.client.get(reverse(pattern.name))
            self.assertEqual(response.status_code, 200)




