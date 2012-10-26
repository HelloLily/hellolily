# Django imports
from django.db import models
from django_fields.fields import EncryptedCharField, EncryptedEmailField
from django.utils.translation import ugettext as _

# Lily imports
from lily.messages.models import Message, SocialMediaAccount
from lily.settings import EMAIL_ATTACHMENT_UPLOAD_TO
from lily.tenant.models import Tenant, TenantMixin


class EmailProvider(models.Model):
    """
    A provider contains the connection information for an account.

    """
    retrieve_host = models.CharField(max_length=32)
    retrieve_port = models.IntegerField(default=993)

    send_host = models.CharField(max_length=32)
    send_port = models.IntegerField(default=587)
    send_use_tls = models.BooleanField(default=True)


    def __unicode__(self):
        return self.retrieve_host


    class Meta:
        verbose_name = _('-email provider')
        verbose_name_plural = _('e-mail providers')


class EmailAccount(SocialMediaAccount):
    """
    An e-mail account which represents a single inbox.

    """
    provider = models.ForeignKey(EmailProvider, related_name='email_accounts')
    name = models.CharField(max_length=255)
    email = EncryptedEmailField(max_length=255)

    # Login credentials
    username = EncryptedCharField(max_length=255)
    password = EncryptedCharField(max_length=255)


    def sync(self, blocking=False):
        from lily.messages.email.tasks import import_account
        result = import_account.delay(self)

        if blocking:
            return result.get()
        return

    def update(self, blocking=False):
        from lily.messages.email.tasks import update_account
        result = update_account.delay(self)

        if blocking:
            return result.get()
        return


    def __unicode__(self):
        return self.name if self.name else self.email


    class Meta:
        verbose_name = _('e-mail account')
        verbose_name_plural = _('e-mail accounts')


class EmailAttachment(models.Model):
    """
    An attachment that can come with an e-mail message.

    """
    attachment = models.FileField(upload_to=EMAIL_ATTACHMENT_UPLOAD_TO)


    def __unicode__(self):
        return self.name if self.name else self.email


    class Meta:
        verbose_name = _('e-mail attachment')
        verbose_name_plural = _('e-mail attachments')


class EmailMessage(Message):
    """
    Store an e-mail message with all possible headers.

    -- Beware --
    -- Almost everything can be blank or null. You can never be certain everything is provided.

    """
    private = models.BooleanField(default=False)
    uid = models.IntegerField()

    message_flags = models.CharField(max_length=255, blank=True, default='')
    subject = models.CharField(max_length=255, blank=True, default='')

    # The plain from string plus the parsed email and name. If provided the original sender.
    from_string = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255)
    from_name = models.CharField(max_length=255)
    sender = models.CharField(max_length=255, blank=True, default='')

    # Gmail specific message info.
    message_id = models.CharField(max_length=255, blank=True, default='')
    thread_id = models.CharField(max_length=255, blank=True, default='')

    # Delivery details.
    delivered_to = models.CharField(max_length=255, blank=True, default='')
    to = models.CharField(max_length=255, blank=True, default='')
    cc = models.CharField(max_length=255, blank=True, default='')
    bcc = models.CharField(max_length=255, blank=True, default='')

    # Details on received stuff.
    received = models.CharField(max_length=255, blank=True, default='')
    received_spf = models.CharField(max_length=255, blank=True, default='')

    # The message itself.
    content_type = models.CharField(max_length=255)
    content_length = models.CharField(max_length=255, blank=True, default='')
    message_html = models.TextField(blank=True, default='')
    message_text = models.TextField(blank=True, default='')

    # Message attachements.
    mime_version = models.CharField(max_length=255, blank=True, default='')
    message_attachements = models.ManyToManyField(EmailAttachment)

    # Random headers from e-mail message.
    return_path = models.CharField(max_length=255, blank=True, default='')
    authentication_results = models.CharField(max_length=255, blank=True, default='')
    content_transfer_encoding = models.CharField(max_length=255, blank=True, default='')
    domainkey_signature = models.CharField(max_length=255, blank=True, default='')
    dkim_signature = models.CharField(max_length=255, blank=True, default='')
    precedence = models.CharField(max_length=255, blank=True, default='')
    references = models.CharField(max_length=255, blank=True, default='')
    user_agent = models.CharField(max_length=255, blank=True, default='')
    in_reply_to = models.CharField(max_length=255, blank=True, default='')
    bounces_to = models.CharField(max_length=255, blank=True, default='')
    errors_to = models.CharField(max_length=255, blank=True, default='')
    keywords = models.CharField(max_length=255, blank=True, default='')
    comments = models.CharField(max_length=255, blank=True, default='')
    encrypted = models.CharField(max_length=255, blank=True, default='')
    priority = models.CharField(max_length=255, blank=True, default='')
    reply_by = models.CharField(max_length=255, blank=True, default='')
    sensitivity = models.CharField(max_length=255, blank=True, default='')
    language = models.CharField(max_length=255, blank=True, default='')
    list_unsubscribe = models.CharField(max_length=255, blank=True, default='')

    # Custom headers??
    x_originating_ip = models.CharField(max_length=255, blank=True, default='')
    x_dsncontext = models.CharField(max_length=255, blank=True, default='')
    x_linkedin_fbl = models.CharField(max_length=255, blank=True, default='')
    x_linkedin_class = models.CharField(max_length=255, blank=True, default='')
    x_linkedin_template = models.CharField(max_length=255, blank=True, default='')
    x_virus_scanned = models.CharField(max_length=255, blank=True, default='')
    x_php_originating_script = models.CharField(max_length=255, blank=True, default='')
    x_priority = models.CharField(max_length=255, blank=True, default='')
    x_destination_id = models.CharField(max_length=255, blank=True, default='')
    x_mailingid = models.CharField(max_length=255, blank=True, default='')
    x_smfbl = models.CharField(max_length=255, blank=True, default='')
    x_report_abuse = models.CharField(max_length=255, blank=True, default='')
    x_virtualservergroup = models.CharField(max_length=255, blank=True, default='')
    x_virtualserver = models.CharField(max_length=255, blank=True, default='')
    x_mailer = models.CharField(max_length=255, blank=True, default='')
    x_smheadermap = models.CharField(max_length=255, blank=True, default='')
    x_sendgrid_eid = models.CharField(max_length=255, blank=True, default='')
    x_google_dkim_signature = models.CharField(max_length=255, blank=True, default='')
    x_sfdc_interface = models.CharField(max_length=255, blank=True, default='')
    x_sfdc_binding = models.CharField(max_length=255, blank=True, default='')
    x_sfdc_user = models.CharField(max_length=255, blank=True, default='')
    x_sfdc_tls_norelay = models.CharField(max_length=255, blank=True, default='')
    x_sender = models.CharField(max_length=255, blank=True, default='')
    x_mail_abuse_inquiries = models.CharField(max_length=255, blank=True, default='')
    x_sfdc_lk = models.CharField(max_length=255, blank=True, default='')
    x_twitterimpressionid = models.CharField(max_length=255, blank=True, default='')
    x_dkim = models.CharField(max_length=255, blank=True, default='')
    x_facebook_notify = models.CharField(max_length=255, blank=True, default='')
    x_facebook_priority = models.CharField(max_length=255, blank=True, default='')
    x_facebook = models.CharField(max_length=255, blank=True, default='')


    def get_template(self):
        return 'messages/email/message_row.html'


    def __unicode__(self):
        return u'%s %s %s'.strip() % (self.uid, self.from_string, self.subject)


    class Meta:
        verbose_name = _('e-mail message')
        verbose_name_plural = _('e-mail messages')


class EmailTemplate(TenantMixin):
    """
    Emails can be composed using templates.
    A template is a predefined email in which parameters can be dynamically inserted.

    """
    name = models.CharField(verbose_name=_('template name'), max_length=255)
    body = models.TextField(verbose_name=_('message body'))


    def __unicode__(self):
        return u'%s' % self.name


    class Meta:
        verbose_name = _('e-mail template')
        verbose_name_plural = _('e-mail templates')


class EmailTemplateParameters(models.Model):
    """
    All template parameters are stored in the database, a parameter is a dynamically filled part of a template.
    This models contains those parameters and, if set, the default value of that parameter.

    Default values can be static or dynamic, which one it is is stored in the default_value syntax:
        static  = 'static:value'
        dynamic = 'dynamic:model/pk/field'

    """
    template = models.ForeignKey(EmailTemplate, verbose_name=_(''), related_name='parameters')
    name = models.CharField(verbose_name=_('parameter name'), max_length=255)
    default_value = models.CharField(verbose_name=_('default parameter value'), max_length=255, blank=True)


    def __unicode__(self):
        return u'%s - %s' % (self.name, self.default_value)


    class Meta:
        verbose_name = _('e-mail template parameter')
        verbose_name_plural = _('e-mail template parameters')