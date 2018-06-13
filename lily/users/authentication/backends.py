from django.contrib.auth.backends import ModelBackend

from lily.users.models import LilyUser


class LilyModelBackend(ModelBackend):
    """
    Authenticates against LilyUsers.

    The `all_objects` manager is used because the normal one filters on tenants, which is not available here.
    """

    def authenticate(self, request, **credentials):
        username = credentials.get('username', None)
        password = credentials.get('password', None)

        if not all([username, password]):
            # If we didn't receive password and username, just return.
            return

        try:
            user = LilyUser.all_objects.get_by_natural_key(username.lower())
        except LilyUser.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            LilyUser().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = LilyUser.all_objects.get(pk=user_id)
        except LilyUser.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None


class LilySocialBackend(ModelBackend):
    """
    Log a user in using a social provider.

    Social logins validate the password using the provider, so we trust that we can match on email only.
    """

    def authenticate(self, request, **credentials):
        username = credentials.get('social_username', None)

        if not username:
            return

        try:
            user = LilyUser.all_objects.get_by_natural_key(username.lower())
        except LilyUser.DoesNotExist:
            return
        else:
            if self.user_can_authenticate(user):
                return user

    def get_user(self, user_id):
        try:
            user = LilyUser.all_objects.get(pk=user_id)
        except LilyUser.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None
