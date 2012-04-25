from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model


class EmailAuthenticationBackend(ModelBackend):
    """
    Authenticate a CustomUser with e-mail address instead of username.
    """
    def authenticate(self, username=None, password=None, no_pass=False):
        """
        Check if the user is properly authenticated, either logging in by e-mail address 
        and password or programmatically logged in (e.g. upon activation of account) 
        using no_pass=True.
        """
        try:
            email = username
            user = self.user_class.objects.get(
                                contact__email_addresses__email_address__iexact=email, 
                                contact__email_addresses__is_primary=True
            )
            
            if(user.is_active) and (user.check_password(password) or no_pass):
                return user
            return None
        except self.user_class.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """
        Return the proper instance of CustomUser for given user_id.
        """
        try:
            return self.user_class.objects.get(pk=user_id)
        except self.user_class.DoesNotExist:
            return None
        
    @property
    def user_class(self):
        """
        Determine which user model to use for authentication etc.
        """
        if not hasattr(self, '_user_class'):
            self._user_class = get_model(*settings.CUSTOM_USER_MODEL.split('.', 2))            
            if not self._user_class:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_class
        