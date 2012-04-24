from django.test import TestCase
from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.users.models import CustomUser
from lily.utils.models import EmailAddress


class Test(TestCase):    
    
    def test_customuser_set_email(self):
        """
        Test the pre_save signal involving e-mail addresses for CustomUser.
        This means when setting the attribute 'email', an emailadress instance
        is actually being created and saved when the user instance is saved.
        """
        
        # Create dummy account
        account = Account.objects.create(name='Foo Bar inc.')
        account.email = 'first@account.com'
        
        # Create dummy contact
        contact = Contact.objects.create(first_name='John', last_name='Doe')        
        contact.save()
        
        # Create dummy user
        u = CustomUser()
        u.contact = contact
        u.account = account
        u.username = 'John'
        u.set_password('123456')
        
        # The attribute being tested
        u.email = 'first@user.com'
        
        # assert email is not saved yet
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        # Save email
        u.save()
        
        # assert email equals first@user.com
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('first@user.com', email)
        
        # change and save email
        u.email = 'second@user.com'
        u.save()
        
        # assert email equals second@user.com
        email = None
        try:
            email = u.contact.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@user.com', email)
        
        # change email (don't save)
        u.email = 'third@user.com'
        
        # assert email still equals second@user.com 
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
        This means when setting the attribute 'email', an emailadress instance
        is actually being created and saved when the user instance is saved.
        """
        
        # Create dummy account
        account = Account.objects.create(name='Foo Bar inc.')
        account.email = 'first@account.com'
        
        # assert email is not saved yet
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual(None, email)
        
        # Save email
        account.save()
        
        # assert email equals first@account.com
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('first@account.com', email)
        
        # change and save email
        account.email = 'second@account.com'
        account.save()
        
        # assert email equals second@account.com
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)
        
        # change email (don't save)
        account.email = 'third@account.com'
        
        # assert email still equals second@user.com 
        email = None
        try:
            email = account.email_addresses.get(is_primary=True)
            email = email.email_address 
        except EmailAddress.DoesNotExist:
            pass        
        self.assertEqual('second@account.com', email)