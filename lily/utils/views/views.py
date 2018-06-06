import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.urls import reverse_lazy, reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.base import TemplateView, RedirectView

from lily.accounts.models import Account
from lily.cases.models import Case
from lily.contacts.models import Contact
from lily.deals.models import Deal
from lily.messaging.email.models.models import EmailAccount, EmailAttachment
from lily.users.models import LilyUser
from lily.utils.models.models import PhoneNumber
from lily.utils.functions import has_required_tier
from ..forms import SugarCsvImportForm
from ..tasks import import_sugar_csv


logger = logging.getLogger(__name__)


class SugarCsvImportView(LoginRequiredMixin, FormView):
    http_method_names = ['get', 'post']
    form_class = SugarCsvImportForm
    template_name = 'form.html'
    success_url = reverse_lazy('sugarcsvimport')

    def form_valid(self, form):
        path = self.write_to_tmp(form.cleaned_data.get('csvfile'))

        sugar_import = form.cleaned_data.get('sugar_import')

        import_sugar_csv.apply_async(args=(
            form.cleaned_data.get('model'),
            path,
            self.request.user.tenant_id,
            sugar_import,
        ))

        messages.info(self.request, _('Import started, you should see results in de appropriate list'))

        return super(SugarCsvImportView, self).form_valid(form)

    def write_to_tmp(self, in_memory_uploaded_file):
        i = 0
        file_name = None
        while True:
            file_name = '%s_%s' % (in_memory_uploaded_file.name, i)
            if not default_storage.exists(file_name):
                break
            else:
                i += 1
        file = default_storage.open(file_name, 'w+')
        for chunk in in_memory_uploaded_file.chunks():
            file.write(chunk)
        file.close()
        return file_name


class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user.info.registration_finished:
            # User is authenticated but has not finished the registration process, so redirect there.
            return HttpResponseRedirect(reverse('register'))

        return super(BaseView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        account_admin = self.request.user.tenant.admin.full_name

        kwargs = super(BaseView, self).get_context_data(**kwargs)
        kwargs.update({
            'INTERCOM_APP_ID': settings.INTERCOM_APP_ID,
            'SENTRY_FRONTEND_PUBLIC_DSN': settings.SENTRY_FRONTEND_PUBLIC_DSN,
            'BILLING_ENABLED': settings.BILLING_ENABLED,
            'SLACK_LILY_CLIENT_ID': settings.SLACK_LILY_CLIENT_ID,
            'SEGMENT_PYTHON_SOURCE_WRITE_KEY': settings.SEGMENT_PYTHON_SOURCE_WRITE_KEY,
            'SEGMENT_JS_SOURCE_WRITE_KEY': settings.SEGMENT_JS_SOURCE_WRITE_KEY,
            'DEBUG': settings.DEBUG,
            'account_admin': account_admin,
        })

        case_count = Case.objects.count()
        deal_count = Deal.objects.count()

        kwargs.update({
            'object_counts': {
                'cases': case_count,
                'deals': deal_count,
            }
        })

        if not has_required_tier(1):
            account_count = Account.objects.filter(is_deleted=False).count()
            contact_count = Contact.objects.filter(is_deleted=False).count()
            email_account_count = EmailAccount.objects.filter(is_deleted=False).count()

            kwargs.update({
                'limit_reached': {
                    'accounts': account_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT,
                    'contacts': contact_count >= settings.FREE_PLAN_ACCOUNT_CONTACT_LIMIT,
                    'email_accounts': email_account_count >= settings.FREE_PLAN_EMAIL_ACCOUNT_LIMIT,
                },
            })

        return kwargs


class RedirectAccountContactView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        phone_nr_list = PhoneNumber.objects.filter(
            number=kwargs.get('phone_nr'),
            status=PhoneNumber.ACTIVE_STATUS
        )

        for phone_nr in phone_nr_list:
            account = phone_nr.account_set.filter(tenant=self.request.user.tenant).first()
            if account:
                return '/#/accounts/%s' % account.id

            contact = phone_nr.contact_set.filter(tenant=self.request.user.tenant).first()
            if contact:
                return '/#/contacts/%s' % contact.id

        return None


class DownloadRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False
    mapping = {
        'email': {
            'model_cls': EmailAttachment,
            'fields': ('attachment', ),
        },
        'profile': {
            'model_cls': LilyUser,
            'fields': ('picture', ),
        },
    }

    def get_redirect_url(self, *args, **kwargs):
        field = getattr(self.instance, self.field_name)
        return field.url  # Let the storage backend generate an url for us.

    def get(self, request, *args, **kwargs):
        self.model_name = kwargs.pop('model_name')
        self.field_name = kwargs.pop('field_name')
        self.object_id = kwargs.pop('object_id')

        if self.model_name not in self.mapping.keys():
            return Http404()
        if self.field_name not in self.mapping[self.model_name]['fields']:
            return Http404()

        self.instance = get_object_or_404(self.mapping[self.model_name]['model_cls'], pk=self.object_id)

        return super(DownloadRedirectView, self).get(request, *args, **kwargs)
