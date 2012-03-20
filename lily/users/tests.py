"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from lily.users.models import UserModel
from lily.contacts.models import ContactModel
from lily.utils.models import EmailAddressModel


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
    
    
    def test_user_inheritance(self):
        """
        """
        
        email = EmailAddressModel.objects.create(email_address='test@domain.com', is_primary=True)
        
        contact = ContactModel.objects.create(first_name='John', last_name='Doe')
        contact.email_addresses.add(email)
        
        contact.save()
        
        u = UserModel()
        u.contact = contact
        u.username = 'John'
        u.set_password('123456')
        u.save()
        
        u = UserModel.objects.get(username='John')
        
        u.contact = contact
        
        print "'%s'" % u.email