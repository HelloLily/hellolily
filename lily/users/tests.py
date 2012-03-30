"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from lily.accounts.models import AccountModel
from lily.contacts.models import ContactModel
from lily.users.models import UserModel
from lily.utils.models import EmailAddressModel


class SimpleTest(TestCase):    
    
    def test_usermodel_set_email(self):
        """
        Test the pre_save signal involving e-mail addresses for UserModel.
        """
        
        contact = ContactModel.objects.create(first_name='John', last_name='Doe')        
        contact.save()
        
        u = UserModel()
        u.contact = contact
        u.username = 'John'
        u.set_password('123456')
        u.email = 'first@user.com'
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        u.save()
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('first@user.com', email)
        
        u.email = 'second@user.com'
        u.save()
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('second@user.com', email)
        
        u.email = 'third@user.com'
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('second@user.com', email)
    
    def test_accountmodel_set_email(self):
        """
        Test the pre_save signal involving e-mail addresses for AccountModel.
        """
        
        account = AccountModel.objects.create(name='Foo Bar inc.', website='http://foobar.org')
        account.email = 'first@account.com' 
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        account.save()
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('first@account.com', email)
        
        account.email = 'second@account.com'
        account.save()
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)
        
        account.email = 'third@account.com'
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddressModel.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)