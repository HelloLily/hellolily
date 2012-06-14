from django.db import models
from django_fields.fields import EncryptedCharField, EncryptedEmailField
from django.utils.translation import ugettext as _


class Provider(models.Model):
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


class EmailAccount(models.Model):
    """
    An e-mail account which represents a single inbox.

    """
    provider = models.ForeignKey(Provider, related_name='email_accounts')
    name = models.CharField(max_length=255)
    email = EncryptedEmailField(max_length=255)

    # Login credentials
    username = EncryptedCharField(max_length=255)
    password = EncryptedCharField(max_length=255)


    def __unicode__(self):
        return self.name if self.name else self.email


    class Meta:
        verbose_name = _('-email account')
        verbose_name_plural = _('e-mail accounts')


class EmailMessage(models.Model):
    """
    Store an e-mail message with all possible headers.

    -- Beware --
    -- Almost everything can be blank or null. You can never be certain everything is provided.

    """
    account = models.ForeignKey(EmailAccount, related_name='messages')
    private = models.BooleanField(default=False)
    uid = models.IntegerField()

    # Gmail specific basic message info.
    message_id = models.CharField(max_length=255)
    message_flags = models.CharField(max_length=255)
    thread_id = models.CharField(max_length=255)

    # Subject of message.
    subject = models.CharField(max_length=255)

    # Delivery details.
    delivered_to = models.CharField(max_length=255)
    to = models.CharField(max_length=255)
    cc = models.CharField(max_length=255)
    bcc = models.CharField(max_length=255)

    # The plain string of who sent the mail and the email and name parsed from that string.
    from_string = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255)
    from_name = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)

    # Details on date sent and received and stuff.
    date = models.CharField(max_length=255)
    received = models.CharField(max_length=255)
    received_spf = models.CharField(max_length=255)

    # The message itself.
    content_type = models.CharField(max_length=255)
    content_length = models.CharField(max_length=255)
    message_html = models.CharField(max_length=255)
    message_text = models.CharField(max_length=255)

    # Message attachements.
    mime_version = models.CharField(max_length=255)
    message_attachements = models.CharField(max_length=255)

    # Random headers from e-mail message.
    return_path = models.CharField(max_length=255)
    authentication_results = models.CharField(max_length=255)
    content_transfer_encoding = models.CharField(max_length=255)
    domainkey_signature = models.CharField(max_length=255)
    dkim_signature = models.CharField(max_length=255)
    precedence = models.CharField(max_length=255)
    references = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255)
    in_reply_to = models.CharField(max_length=255)
    bounces_to = models.CharField(max_length=255)
    errors_to = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    comments = models.CharField(max_length=255)
    encrypted = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
    reply_by = models.CharField(max_length=255)
    sensitivity = models.CharField(max_length=255)
    language = models.CharField(max_length=255)
    message_type = models.CharField(max_length=255)
    list_unsubscribe = models.CharField(max_length=255)

    # Custom headers??
    x_originating_ip = models.CharField(max_length=255)
    x_dsncontext = models.CharField(max_length=255)
    x_linkedin_fbl = models.CharField(max_length=255)
    x_linkedin_class = models.CharField(max_length=255)
    x_linkedin_template = models.CharField(max_length=255)
    x_virus_scanned = models.CharField(max_length=255)
    x_php_originating_script = models.CharField(max_length=255)
    x_priority = models.CharField(max_length=255)
    x_destination_id = models.CharField(max_length=255)
    x_mailingid = models.CharField(max_length=255)
    x_smfbl = models.CharField(max_length=255)
    x_report_abuse = models.CharField(max_length=255)
    x_virtualservergroup = models.CharField(max_length=255)
    x_virtualserver = models.CharField(max_length=255)
    x_mailer = models.CharField(max_length=255)
    x_smheadermap = models.CharField(max_length=255)
    x_sendgrid_eid = models.CharField(max_length=255)
    x_google_dkim_signature = models.CharField(max_length=255)
    x_sfdc_interface = models.CharField(max_length=255)
    x_sfdc_binding = models.CharField(max_length=255)
    x_sfdc_user = models.CharField(max_length=255)
    x_sfdc_tls_norelay = models.CharField(max_length=255)
    x_sender = models.CharField(max_length=255)
    x_mail_abuse_inquiries = models.CharField(max_length=255)
    x_sfdc_lk = models.CharField(max_length=255)
    x_twitterimpressionid = models.CharField(max_length=255)
    x_dkim = models.CharField(max_length=255)
    x_facebook_notify = models.CharField(max_length=255)
    x_facebook_priority = models.CharField(max_length=255)
    x_facebook = models.CharField(max_length=255)


    def __unicode__(self):
        return u'%s %s %s'.strip() % (self.uid, self.from_string, self.subject)


    class Meta:
        verbose_name = _('-email message')
        verbose_name_plural = _('e-mail messages')