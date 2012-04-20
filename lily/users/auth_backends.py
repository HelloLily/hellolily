from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

class UserModelBackend(ModelBackend):
    """
    Authenticate the user, instead of using the default User model we use the
    CustomUser model and return this as well.
    """
    def authenticate(self, username=None, password=None, no_pass=False):
        """
        Check if the user is properly authenticated, either by username
        and password check (login), or code login (upon activation of account)
        """
        try:
            user = self.user_class.objects.get(username=username)
            if (user.is_active) and (user.check_password(password) or no_pass):
                return user
        except self.user_class.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Return the custom user model
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