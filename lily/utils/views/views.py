import json
import logging

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from django.views.generic.base import View, TemplateView, RedirectView

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


class ArchiveView(View):
    """
    Abstract view that makes it possible to archive an item which redirects to success_url afterwards.

    Needs a post, with one or more ids[] for the instance to be archived.
    Subclass needs to set `success_url` or override `get_success_url`.
    """
    model = None
    queryset = None
    success_url = None  # Needs to be set in subclass, or override get_success_url.
    http_method_names = ['post']

    def get_object_pks(self):
        """
        Get primary key(s) from POST.

        Raises:
            AttributeError: If no object_pks can be retrieved.
        """
        object_pks = self.request.POST.get('ids[]', None)
        if not object_pks:
            # No objects posted.
            raise AttributeError(
                'Generic Archive view %s must be called with at least one object pk.'
                % self.__class__.__name__
            )
        # Always return as a list.
        return object_pks.split(',')

    def get_queryset(self):
        """
        Default function from MultipleObjectMixin.get_queryset, and slightly modified.

        Raises:
            ImproperlyConfigured: If there is no queryset or model set.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "'%s' must define 'queryset' or 'model'"
                % self.__class__.__name__
            )

        # Filter the queryset with the pk's posted.
        queryset = queryset.filter(pk__in=self.get_object_pks())

        return queryset

    def get_success_message(self, n):
        """
        Should be overridden if there needs to be a success message after archiving objects.

        Args:
            n (int): Number of objects that were affected by the action.
        """
        pass

    def get_success_url(self):
        """
        Returns the succes_url if set, otherwise will raise ImproperlyConfigured.

        Returns:
            the success_url.
        """
        self.success_url = self.request.POST.get('success_url', self.success_url)
        if self.success_url is None:
            raise ImproperlyConfigured(
                "'%s' must define a success_url" % self.__class__.__name__
            )
        return self.success_url

    def archive(self, archive=True, **kwargs):
        """
        Archives all objects found.

        Returns:
            HttpResponseRedirect object set to success_url.
        """
        queryset = self.get_queryset()
        kwargs.update({'is_archived': archive})
        queryset.update(**kwargs)
        for item in queryset.all():
            item.save()
        self.get_success_message(len(queryset))

        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        """
        Catch post to start archive process.
        """
        return self.archive(archive=True)


class UnarchiveView(ArchiveView):
    """
    Abstract view that makes it possible to un-archive an item which redirects to success_url afterwards.

    Needs a post, with at least one pk for the instance to be archived.
    """
    def post(self, request, *args, **kwargs):
        """
        Catch post to start un-archive process.
        """
        return self.archive(archive=False)


class AjaxUpdateView(LoginRequiredMixin, View):
    """
    View that provides an option to update models based on a url and POST data.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            app_name = kwargs.pop('app_name')
            model_name = kwargs.pop('model_name').lower().capitalize()
            object_id = kwargs.pop('object_id')

            model = apps.get_model(app_name, model_name)
            instance = model.objects.get(pk=object_id)

            changed = False
            for key, value in request.POST.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                    changed = True

            if changed:
                instance.save()
        except:
            raise Http404()

        # Return response
        return HttpResponse(json.dumps({}), content_type='application/json')


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


class RedirectSetMessageView(RedirectView):
    message = ''
    message_level = 'info'

    def get_message_level(self):
        if not self.message_level:
            raise NotImplementedError(_('Didn\'t set the correct message level'))

        return self.message_level

    def get_message(self):
        if not self.message:
            raise NotImplementedError(_('No message has been set'))

        return self.message

    def dispatch(self, request, *args, **kwargs):
        message_level = self.get_message_level()
        message = self.get_message()
        getattr(messages, message_level)(request, message)

        return super(RedirectSetMessageView, self).dispatch(request, *args, **kwargs)


class BaseView(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        account_admin = self.request.user.tenant.admin.full_name

        kwargs = super(BaseView, self).get_context_data(**kwargs)
        kwargs.update({
            'INTERCOM_APP_ID': settings.INTERCOM_APP_ID,
            'SENTRY_FRONTEND_PUBLIC_DSN': settings.SENTRY_FRONTEND_PUBLIC_DSN,
            'BILLING_ENABLED': settings.BILLING_ENABLED,
            'SLACK_LILY_CLIENT_ID': settings.SLACK_LILY_CLIENT_ID,
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
