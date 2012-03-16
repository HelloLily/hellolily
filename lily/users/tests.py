"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User
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
        
        email = EmailAddressModel.objects.create(email_address='c.poppema@gmail.com', is_primary=True)
        
        contact = ContactModel.objects.create(first_name='Cornelis', last_name='Poppema')
        contact.email_addresses.add(email)
        
        contact.save()
        
        u = UserModel()
        u.contact = contact
        u.username = 'Cornelis'
        u.set_password('123456')
        u.save()
        
        u = UserModel.objects.get(username='Cornelis')
        
        u.contact = contact
        
        print "'%s'" % u.email
        
#        email = "c.poppema@gmail.com"
#UserModel.objects.filter(contact__email_addresses__email_address__iexact=email, contact__email_addresses__is_primary=True, is_active=True)
#        print user