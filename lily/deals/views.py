import datetime
from datetime import date, timedelta

import anyjson
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from pytz import timezone

from lily.accounts.models import Account
from lily.utils.functions import is_ajax
from lily.utils.views import AjaxUpdateView
from lily.utils.views.mixins import LoginRequiredMixin

from .forms import CreateUpdateDealForm
from .models import Deal


class ArchiveDealsView(LoginRequiredMixin, AjaxUpdateView):
    """
    Archives a deal.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the stage and closed_date attributes for a Deal object.
        """
        try:
            if 'id' in request.POST.keys():
                instance = Deal.objects.get(pk=int(request.POST['id']))

                instance.is_archived = True

                instance.save()
            else:
                messages.error(self.request, _('Deal could not be archived'))
                raise Http404()
        except:
            messages.error(self.request, _('Deal could not be archived'))
            raise Http404()
        else:
            message = _('Deal has been archived')
            messages.success(self.request, message)

            return HttpResponse(anyjson.serialize({'archived': 'true'}), content_type='application/json')


class UnarchiveDealsView(LoginRequiredMixin, AjaxUpdateView):
    """
    Unarchives a deal.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the stage and closed_date attributes for a Deal object.
        """
        try:

            if 'id' in request.POST.keys():
                instance = Deal.objects.get(pk=int(request.POST['id']))

                instance.is_archived = False

                instance.save()
            else:
                messages.error(self.request, _('Deal could not be unarchived'))
                raise Http404()
        except:
            messages.error(self.request, _('Deal could not be unarchived'))
            raise Http404()
        else:
            message = _('Deal has been unarchived')
            messages.success(self.request, message)

            return HttpResponse(anyjson.serialize({'archived': 'false'}), content_type='application/json')


class CreateUpdateDealMixin(LoginRequiredMixin):
    """
    Base class for CreateDealView and UpdateDealView.
    """
    form_class = CreateUpdateDealForm
    model = Deal

    def get_context_data(self, **kwargs):
        """
        Provide an url to go back to.
        """
        kwargs = super(CreateUpdateDealMixin, self).get_context_data(**kwargs)
        if not is_ajax(self.request):
            kwargs.update({
                'back_url': self.get_success_url(),
            })

        return kwargs

    def form_valid(self, form):
        """
        Overloading super().form_valid to add success message after editing.
        """
        # Save instance.
        response = super(CreateUpdateDealMixin, self).form_valid(form)

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has successfully been submitted.
        """
        return '/#/deals'


class CreateDealView(CreateUpdateDealMixin, CreateView):
    def dispatch(self, request, *args, **kwargs):
        """
        For AJAX calls, use a different form and template.
        """

        return super(CreateDealView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        Set the initials for the form
        """
        initial = super(CreateDealView, self).get_initial()

        # If the Deal is created from an Account, initialize the form with data from that Account.
        account_pk = self.kwargs.get('account_pk', None)
        if account_pk:
            try:
                account = Account.objects.get(pk=account_pk)
            except Account.DoesNotExist:
                pass
            else:
                initial.update({'account': account})

                deal_count = Deal.objects.filter(account=account).count()

                # If the account is newer than 7 days and it doesn't have any deals; we mark it as a new business.
                if deal_count == 0 and account.created.date() > date.today() - timedelta(days=7):
                    initial.update({'new_business': True})

        return initial

    def form_valid(self, form):
        # Saves the instance
        response = super(CreateDealView, self).form_valid(form)

        # Show save message
        message = _('%s (Deal) has been created.') % self.object.name
        messages.success(self.request, message)

        if is_ajax(self.request):
            # Reload when user is in the deal list
            response = anyjson.serialize({
                'error': False,
                'redirect_url': self.get_success_url()
            })
            return HttpResponse(response, content_type='application/json')

        return response

    def form_invalid(self, form):
        response = self.render_to_response(self.get_context_data(form=form))
        if is_ajax(self.request):
            response = anyjson.serialize({
                'error': True,
                'html': response.rendered_content
            })
            return HttpResponse(response, content_type='application/json')

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has successfully been submitted.
        """
        if self.object:
            return '/#/deals/' + str(self.object.id)
        else:
            return '/#deals'


class UpdateDealView(CreateUpdateDealMixin, UpdateView):
    model = Deal

    def form_valid(self, form):
        # Saves the instance
        response = super(UpdateDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been updated.') % self.object.name)

        return response

    def get_success_url(self):
        """
        Get the url to redirect to after this form has successfully been submitted.
        """
        return '/#/deals'


class UpdateAndUnarchiveDealView(CreateUpdateDealMixin, UpdateView):
    """
    Allows a deal to be unarchived and edited if needed
    """
    model = Deal

    def dispatch(self, request, *args, **kwargs):
        # Change form and template for ajax calls
        if is_ajax(request):
            self.form_class = CreateUpdateDealForm
            self.template_name = 'deals/deal_unarchive_form.html'

        return super(UpdateAndUnarchiveDealView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Makes sure the deal gets unarchived when the object is saved
        self.object.is_archived = False

        # Saves the instance
        super(UpdateAndUnarchiveDealView, self).form_valid(form)

        # Show save message
        messages.success(self.request, _('%s (Deal) has been unarchived.') % self.object.name)

        response = anyjson.serialize({
            'error': False,
            'redirect_url': self.get_success_url()
        })
        return HttpResponse(response, content_type='application/json')

    def get_success_url(self):
        return reverse('deal_details', kwargs={
            'pk': self.object.id
        })


class DeleteDealView(LoginRequiredMixin, DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Deal

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        # Show delete message
        messages.success(self.request, _('%s (Deal) has been deleted.') % self.object.name)

        redirect_url = self.get_success_url()

        response = anyjson.serialize({
            'error': False,
            'redirect_url': redirect_url
        })
        return HttpResponse(response, content_type='application/json')

    def get_success_url(self):
        return '/#/deals'


class UpdateStageAjaxView(LoginRequiredMixin, AjaxUpdateView):
    """
    View that updates the stage-field of a Deal.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Overloading post to update the stage and closed_date attributes for a Deal object.
        """
        try:
            object_id = kwargs.pop('pk')
            instance = Deal.objects.get(pk=object_id)

            if 'stage' in request.POST.keys() and len(request.POST.keys()) == 1:
                instance.stage = int(request.POST['stage'])

                if instance.stage in [Deal.WON_STAGE, Deal.LOST_STAGE]:
                    if not instance.closed_date:
                        instance.closed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
                else:
                    instance.closed_date = None

                instance.save()
            else:
                messages.error(self.request, _('Stage could not be changed'))
                raise Http404()
        except:
            messages.error(self.request, _('Stage could not be changed'))
            raise Http404()
        else:
            message = _('Stage has been changed to') + ' ' + unicode(Deal.STAGE_CHOICES[instance.stage][1])
            messages.success(self.request, message)
            stage = unicode(Deal.STAGE_CHOICES[instance.stage][1])
            # Return response
            if instance.closed_date is None:
                return HttpResponse(anyjson.serialize({'stage': stage}), content_type='application/json')
            else:
                closed_date_local = instance.closed_date.astimezone(timezone(settings.TIME_ZONE))
                response = anyjson.serialize({
                    'closed_date': closed_date_local.strftime('%d %b %y %H:%M'),
                    'stage': stage,
                })
                return HttpResponse(response, content_type='application/json')
