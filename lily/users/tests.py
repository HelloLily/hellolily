from django.test import TestCase

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.users.models import CustomUser
from lily.utils.models import EmailAddress


class SimpleTest(TestCase):    
    
    def test_customuser_set_email(self):
        """
        Test the pre_save signal involving e-mail addresses for CustomUser.
        TODO: re-evaluate and document this file.
        """
        
        contact = Contact.objects.create(first_name='John', last_name='Doe')        
        contact.save()
        
        u = CustomUser()
        u.contact = contact
        u.username = 'John'
        u.set_password('123456')
        u.email = 'first@user.com'
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        u.save()
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('first@user.com', email)
        
        u.email = 'second@user.com'
        u.save()
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@user.com', email)
        
        u.email = 'third@user.com'
        
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@user.com', email)
    
    def test_account_set_email(self):
        """
        Test the pre_save signal involving e-mail addresses for Account.
        """
        
        account = Account.objects.create(name='Foo Bar inc.', website='http://foobar.org')
        account.email = 'first@account.com' 
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        account.save()
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('first@account.com', email)
        
        account.email = 'second@account.com'
        account.save()
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)
        
        account.email = 'third@account.com'
        
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)