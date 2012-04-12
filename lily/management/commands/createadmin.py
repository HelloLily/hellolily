from django.contrib.auth.models import Group, User
from django.core.management.base import NoArgsCommand
from django.db.models.query_utils import Q
from lily.accounts.models import AccountModel
from lily.contacts.models import ContactModel
from lily.users.models import UserModel
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
            
            # Check if a UserModel is linked to this user
            usermodel = UserModel.objects.filter(user_ptr=superUser)
            if usermodel.exists():
                use_existing = False
                while use_existing not in ["yes", "no"]:
                    use_existing = raw_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUser.username)
                use_existing = (use_existing == 'yes')
                if use_existing:
                    # Usermodel already exists, only add it to a group
                    self.add_to_group(usermodel)
                else:
                    # Create brand new usermodel
                    self.create_new()
            else:
                use_existing = False
                while use_existing not in ["yes", "no"]:
                    use_existing = raw_input('Admin found. Use "%s" for a new admin? (yes/no) ' % superUser.username)
                use_existing = (use_existing == 'yes')
                if use_existing:
                    # Create new usermodel using existing user
                    self.create_new(user=superUser)
                else:
                    # Create brand new usermodel
                    self.create_new()
            
        except User.DoesNotExist:
            # Create brand new usermodel
            self.stdout.write('No admins found.\n')
            self.create_new()
        except User.MultipleObjectsReturned:
            use_existing = False
            while use_existing not in ["yes", "no"]:
                use_existing = raw_input('Multiple admins already exists. Create new? (yes/no) ')
            use_existing = (use_existing == 'no')
            if use_existing:
                users = UserModel.objects.filter(~Q(pk__in=User.objects.all().values('pk')))
                if len(users) > 0:
                    for user in users:
                        self.stdout.write('"%s"\n' % user.username)
            
                        username = raw_input('Type in username of the user ')
                        user=users.filter(username=username)
                        self.create_new(user=user)
                else:
                    # TODO: filter directly for users linked to usermodels to prevent this if-statement
                    self.create_new()
            else:
                self.create_new()
    
    def create_new(self, user=None):
        """
        Create an admin with a new account/contact/usermodel.
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
        
        account = AccountModel.objects.create(name=accountname)
        contact = ContactModel.objects.create(first_name=first_name, last_name=last_name)
        
        if user is None:
            usermodel = UserModel()
            usermodel.username = username
            usermodel.email = email
            usermodel.set_password(password2)
        else:
            usermodel = UserModel(user_ptr=user)
            # Transfer values from superclass to subclass
            usermodel.__dict__.update(user.__dict__)
        usermodel.is_superuser = True
        usermodel.contact = contact
        usermodel.account = account
        
        usermodel.save()
        
        if not self.is_user_in_group(usermodel):
            self.add_to_group(usermodel)
        
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
            