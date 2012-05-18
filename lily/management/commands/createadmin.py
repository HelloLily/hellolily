import getpass
from uuid import uuid4

from django.contrib.auth.models import Group
from django.core.management.base import NoArgsCommand
from django.utils.encoding import force_unicode

from lily.accounts.models import Account
from lily.contacts.models import Contact, Function
from lily.tenant.models import Tenant
from lily.users.models import CustomUser


class Command(NoArgsCommand):
    help = """Create a user which can be used to log in to HelloLily. The default superuser that is prompted \
            for after the syncdb command does not have the appropriate permission groups and is missing \
            the essential relation to a custom model used for log in."""
            
    def handle_noargs(self, **options): 
        # First check if there has been created a superuser during syncdb we can use to encapsulate
        # in our own user model.
        superUsers = CustomUser.objects.filter(user_ptr__is_superuser=True)
        
        if len(superUsers) == 0:
            # Create brand new custom user
            self.create_new()
        elif len(superUsers) == 1:            
            # Check if a CustomUser is linked to this user
            customUser = CustomUser.objects.filter(user_ptr=superUsers[0])
            if customUser.exists():
                use_existing = self.ask_for_yes_no_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUsers[0].email)
                if use_existing:
                    # CustomUser already exists, only add it to a group
                    self.add_to_group(customUser)
                else:
                    # Create brand new custom user
                    self.create_new()
            else:
                use_existing = self.ask_for_yes_no_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUsers[0].email)
                if use_existing:
                    # Create new custom user using existing user
                    self.create_new(user=superUsers[0])
                else:
                    # Create brand new custom user
                    self.create_new()
        else:
            create_new = self.ask_for_yes_no_input('Multiple admins already exists. Create new? (yes/no) ')
            if create_new:
                self.create_new()
            else:
                self.stdout.write('Available admins:\n')
                for user in superUsers:
                    self.stdout.write('    %s\n' % user.email)
                    email = None
                    # Let the user choose by e-mail address
                    while email not in superUsers.values_list('contact__email_addresses__email_address', flat=True):
                        email = force_unicode(self.ask_for_input('Type in the e-mail address of the user: '))
                        if email not in superUsers.values_list('contact__email_addresses__email_address', flat=True):
                            self.stdout.write('Unknown e-mail address\n')
                    # Find user by e-mail address
                    user=superUsers.get(contact__email_addresses__email_address__iexact=email)
                    self.create_new(user=user)
    
    def create_new(self, user=None):
        """
        Create an admin with a new account/contact/customuser.
        """
        first_name = self.ask_for_input('Please enter a first name: ')
        last_name = self.ask_for_input('Please enter a last name: ')
        accountname = self.ask_for_input('Please enter an account name: ')
        
        if user is None:
            email_is_unique = False
            email = False
            while not email_is_unique:
                if not email:
                    email = self.ask_for_input('Please enter an e-mail address: ')
                emails = CustomUser.objects.filter(contact__email_addresses__email_address__iexact=email, contact__email_addresses__is_primary=True)
                if len(emails) == 0:
                    email_is_unique = True
                else:
                    email = raw_input('E-mail address already in use, try again: ').strip()
            
            password1 = 0
            password2 = 1
            while password2 != password1:
                password1 = getpass.getpass('Your password: ')
                while password1 is '':
                    password1 = getpass.getpass('Password can\'t be empty: ')
                    
                password2 = getpass.getpass('Confirm password: ')
                while password2 is '':
                    password2 = getpass.getpass('Password can\'t be empty: ')

                if password2 != password1:
                    self.stdout.write('Confirmation failed.\n')
        
        tenant = Tenant.objects.create()
        account = Account.objects.create(name=accountname, tenant=tenant)
        contact = Contact.objects.create(first_name=first_name, last_name=last_name, tenant=tenant)
        function = Function.objects.create(account=account, contact=contact)
        
        if user is None:
            customUser = CustomUser()
            customUser.username = uuid4().get_hex()[:10]
            customUser.primary_email = email
            customUser.set_password(password2)
        else:
            customUser = CustomUser(user_ptr=user)
            # Transfer values from superclass to subclass
            customUser.__dict__.update(user.__dict__)
        customUser.is_superuser = True
        customUser.is_staff = True
        customUser.contact = contact
        customUser.account = account
        customUser.tenant = tenant
        
        customUser.save()
        
        if not self.is_user_in_group(customUser):
            self.add_to_group(customUser)
        
        self.stdout.write('Admin created.\n')
    
    def add_to_group(self, user, group_name='account_admin'):
        """
        Add a user to given group.
        """
        # Get group
        group, created = Group.objects.get_or_create(name='account_admin')
        user.groups.add(group)
    
    def is_user_in_group(self, user, group_name='account_admin'):
        """
        Return True if a user is in a certain group, False otherwise.
        """
        group = Group.objects.filter(name=group_name)
        return group in user.groups.all()            
        
    def ask_for_input(self, question):
        user_input = raw_input(question).strip()
        while user_input is '':
            if not user_input:
                self.stdout.write('Input can\'t be empty: ')
            user_input = raw_input('').strip()
        return user_input
    
    def ask_for_yes_no_input(self, question):
        user_input = self.ask_for_input(question).strip()
        while user_input not in ['yes', 'y', 'no', 'n']:
            if user_input not in ['yes', 'y', 'no', 'n']:
                self.stdout.write('Please answer yes or no: ')
            user_input = raw_input('').strip()
        return (user_input[:1] == 'y')
        