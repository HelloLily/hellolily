from django.contrib.auth.models import Group, User
from django.core.management.base import NoArgsCommand
from django.db.models.query_utils import Q
from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.users.models import CustomUser
import getpass

class Command(NoArgsCommand):
    help = """Create a user which can be used to log in to HelloLily. The default superuser that is prompted \
            for after the syncdb command does not have the appropriate permission groups and is missing \
            the essential relation to a custom model used for log in."""
    
    def handle_noargs(self, **options):
        try: 
            # First check if there has been created a superuser during syncdb we can use to encapsulate
            # in our own user model.
            superUser = User.objects.get(is_superuser=True)
            
            # Check if a CustomUser is linked to this user
            customUser = CustomUser.objects.filter(user_ptr=superUser)
            if customUser.exists():
                use_existing = False
                while use_existing not in ["yes", "no"]:
                    use_existing = raw_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUser.username)
                use_existing = (use_existing == 'yes')
                if use_existing:
                    # CustomUser already exists, only add it to a group
                    self.add_to_group(customUser)
                else:
                    # Create brand new custom user
                    self.create_new()
            else:
                use_existing = False
                while use_existing not in ["yes", "no"]:
                    use_existing = raw_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUser.username)
                use_existing = (use_existing == 'yes')
                if use_existing:
                    # Create new custom user using existing user
                    self.create_new(user=superUser)
                else:
                    # Create brand new custom user
                    self.create_new()
            
        except User.DoesNotExist:
            # Create brand new custom user
            self.stdout.write('No admins found.\n')
            self.create_new()
        except User.MultipleObjectsReturned:
            use_existing = False
            while use_existing not in ["yes", "no"]:
                use_existing = raw_input('Multiple admins already exists. Create new? (yes/no) ')
            use_existing = (use_existing == 'no')
            if use_existing:
                customUsers = CustomUser.objects.filter(~Q(pk__in=User.objects.all().values('pk')))
                if len(customUsers) > 0:
                    for user in customUsers:
                        self.stdout.write('"%s"\n' % user.username)
            
                        username = raw_input('Type in username of the user ')
                        user=customUsers.filter(username=username)
                        self.create_new(user=user)
                else:
                    # TODO: filter directly for users linked to custom users to prevent this if-statement
                    self.create_new()
            else:
                self.create_new()
    
    def create_new(self, user=None):
        """
        Create an admin with a new account/contact/customuser.
        """
        first_name = raw_input('Please enter a first name: ')
        last_name = raw_input('Please enter a last name: ')
        accountname = raw_input('Please enter an account name: ')
        
        if user is None:
            username = raw_input('Please enter a username: ')
            email = raw_input('Please enter an e-mail address: ')
            
            password1 = 0
            password2 = 1
            while password2 != password1:
                password1 = getpass.getpass('Your password: ')
                password2 = getpass.getpass('Confirm password: ')

                if password2 != password1:
                    self.stdout.write('Confirmation failed.\n')
        
        account = Account.objects.create(name=accountname)
        contact = Contact.objects.create(first_name=first_name, last_name=last_name)
        
        if user is None:
            customUser = CustomUser()
            customUser.username = username
            customUser.email = email
            customUser.set_password(password2)
        else:
            customUser = CustomUser(user_ptr=user)
            # Transfer values from superclass to subclass
            customUser.__dict__.update(user.__dict__)
        customUser.is_superuser = True
        customUser.is_staff = True
        customUser.contact = contact
        customUser.account = account
        
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
        try:
            group = Group.objects.get(name=group_name)
            user.groups.get(group)
            return True
        except Group.DoesNotExist:
            return False
            