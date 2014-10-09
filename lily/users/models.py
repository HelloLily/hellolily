from django.contrib import messages
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.signals import user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.contacts.models import Contact
from lily.tenant.models import TenantMixin
from lily.utils.models import EmailAddress
from lily.utils.functions import uniquify
try:
    from lily.tenant.functions import add_tenant
except ImportError:
    from lily.utils.functions import dummy_function as add_tenant


class CustomUser(User, TenantMixin):
    """
    Custom user model, has relation with Contact.
    """
    objects = UserManager()
    contact = models.ForeignKey(Contact, related_name='user')
    account = models.ForeignKey(Account, related_name='user')

    def __unicode__(self):
        return unicode(self.contact)

    @property
    def primary_email(self):
        try:
            if self.contact:
                return self.contact.email_addresses.get(is_primary=True)
        except EmailAddress.DoesNotExist:
            pass
        return u''

    def get_messages_accounts(self, model=None, pk__in=None):
        """
        Returns a list of the users accounts and accounts that are shared with
        this user.

        Also filters out accounts that are deleted and/or have wrong credentials.

        Arguments:
            model (optional): filters the accounts on a specific model type
            pk__in (optional): filters the accounts on specific pks

        Returns:
            list of MessagesAccounts
        """
        # Check cache
        if hasattr(self, '_messages_accounts_%s_%s' % (model, pk__in)):
            return getattr(self, '_messages_accounts_%s_%s' % (model, pk__in))

        from lily.messaging.models import MessagesAccount
        from lily.messaging.email.models import OK_EMAILACCOUNT_AUTH

        # Filter by content type if provided
        if model is not None:
            ctype = ContentType.objects.get_for_model(model)

            # Include shared accounts
            messages_accounts = MessagesAccount.objects.filter(
                Q(is_deleted=False) &
                (
                    # Q(shared_with=1) |
                    Q(shared_with=2, user_group__pk=self.pk) |
                    Q(pk__in=self.messages_accounts.filter(polymorphic_ctype=ctype).values_list('pk'))
                )
            )
        else:
            # Include all type of accounts and include shared accounts
            messages_accounts = MessagesAccount.objects.filter(
                Q(is_deleted=False) &
                (
                    # Q(shared_with=1) |
                    Q(shared_with=2, user_group__pk=self.pk) |
                    Q(pk__in=self.messages_accounts.values_list('pk'))
                )
            )

        if pk__in is not None:
            messages_accounts = messages_accounts.filter(pk__in=pk__in)

        # Uniquify accounts
        messages_accounts = uniquify(messages_accounts.order_by('emailaccount__email__email_address'), filter=lambda x: x.emailaccount.email.email_address)

        # Filter out on EmailAccounts that not have correct credentials and are not owned by us.
        own_or_active_accounts = []
        for account in messages_accounts:
            # Check if account is an emailaccount
            if hasattr(account, 'emailaccount'):
                # Check if account is from user or has correct credentials.
                if account in self.messages_accounts.all() or account.auth_ok is OK_EMAILACCOUNT_AUTH:
                    own_or_active_accounts.append(account)
            else:
                own_or_active_accounts.append(account)

        # Cache for this request.
        setattr(self, '_messages_accounts_%s_%s' % (model, pk__in), own_or_active_accounts)

        return own_or_active_accounts

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['contact']
        permissions = (
            ("send_invitation", _("Can send invitations to invite new users")),
        )


## ------------------------------------------------------------------------------------------------
## Signal listeners
## ------------------------------------------------------------------------------------------------


@receiver(pre_save, sender=CustomUser)
def post_save_customuser_handler(sender, **kwargs):
    """
    If an e-mail attribute was set on an instance of CustomUser, add a primary e-mail address or
    overwrite the existing one.
    """
    instance = kwargs['instance']
    if instance.__dict__.has_key('primary_email'):
        new_email_address = instance.__dict__['primary_email']
        if len(new_email_address.strip()) > 0:
            try:
                # Overwrite existing primary e-mail address
                email = instance.contact.email_addresses.get(is_primary=True)
                email.email_address = new_email_address
                email.save()
            except EmailAddress.DoesNotExist:
                # Add new e-mail address as primary
                email = EmailAddress(email_address=new_email_address, is_primary=True)
                add_tenant(email, instance.tenant)
                email.save()
                instance.contact.email_addresses.add(email)


@receiver(user_logged_out)
def logged_out_callback(sender, **kwargs):
    request = kwargs['request']
    messages.info(request, _('You are now logged out.'))
