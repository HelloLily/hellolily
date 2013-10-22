import operator
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import DeleteView, UpdateView, FormMixin

from lily.contacts.models import Contact
from lily.notes.forms import EditNoteForm, NoteForm
from lily.notes.models import Note
from lily.utils.functions import is_ajax
from lily.utils.models import HistoryListItem
from python_imap.folder import ALLMAIL, IMPORTANT, INBOX, SENT, STARRED


class DeleteNoteView(DeleteView):
    """
    Delete an instance and all instances of m2m relationships.
    """
    model = Note

    def delete(self, request, *args, **kwargs):
        """
        Overloading super().delete to remove the related models and the instance itself.
        """
        self.object = self.get_object()
        self.object.delete()

        # Return response
        return HttpResponse(simplejson.dumps({
            'html': _('The note was successfully deleted.'),
        }), mimetype='application/json')


class EditNoteView(UpdateView):
    model = Note
    form_class = EditNoteForm
    template_name = 'notes/mwsadmin/edit_form.html'
    ajax_template_name = 'notes/mwsadmin/list_item.html'

    def get_success_url(self):
        return reverse('dashboard')

    def form_valid(self, form):
        self.object = form.save()

        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': False,
                'html': render_to_string(self.ajax_template_name, context_instance=context),
            }), mimetype='application/json')

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if is_ajax(self.request):
            context = RequestContext(self.request, self.get_context_data(form=form))
            return HttpResponse(simplejson.dumps({
                'error': True,
                'html': render_to_string(self.ajax_template_name, context_instance=context)
            }), mimetype='application/json')

        return super(EditNoteView, self).form_invalid(form)


class NoteDetailViewMixin(FormMixin, SingleObjectMixin, TemplateResponseMixin, View):
    """
    DetailView for models including a NoteForm to quickly add notes.
    """
    form_class = NoteForm

    def get(self, request, *args, **kwargs):
        """
        Implementing the response for the http method GET.
        """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        context = self.get_context_data(object=self.object, form=form)
        context.update({
            'history_list': self.object.notes.all()
        })

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Implementing the response for the http method POST.
        """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        When adding a note, automatically save the related object and author.
        """
        note = form.save(commit=False)
        note.author = self.request.user
        note.subject = self.object
        note.save()

        return super(NoteDetailViewMixin, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form))

    def get_success_url(self):
        if not hasattr(self, 'success_url_reverse_name'):
            return super(NoteDetailViewMixin, self).get_success_url()

        return reverse(self.success_url_reverse_name, kwargs={ 'pk': self.object.pk })


class HistoryListViewMixin(NoteDetailViewMixin):
    """
    DetailView for models including a NoteForm to quickly add notes.
    """
    form_class = NoteForm
    page_size = 15
    ajax_template = 'mwsadmin/base_list.html'
    list_item_template = 'mwsadmin/base_details_history_list_item.html'

    def get(self, request, *args, **kwargs):
        """
        Implementing the response for the http method GET.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        self.is_ajax = is_ajax(request)

        context = self.get_context_data(object=self.object, form=form)

        if self.is_ajax:
            html = render_to_string(self.ajax_template, {}, context_instance=RequestContext(self.request, context))
            response = HttpResponse(simplejson.dumps({
                'html': html.strip(),
                'hide_button': len(context['list']) < 15,
            }), mimetype='application/json')
        else:
            response = self.render_to_response(context)

        return response

    def get_context_data(self, **kwargs):
        """
        Return the context dictionary used for template rendering.
        """
        context = super(HistoryListViewMixin, self).get_context_data(**kwargs)

        note_content_type_id = ContentType.objects.get_for_model(self.model).pk
        email_address_list = [x.email_address for x in self.object.email_addresses.all()]

        if email_address_list:
            q_object_list = [Q(message__emailmessage__headers__value__contains=x) for x in email_address_list]

            history_list = HistoryListItem.objects.filter(
                (Q(note__content_type=note_content_type_id) & Q(note__object_id=self.object.pk)) |
                (
                    Q(message__emailmessage__folder_identifier=ALLMAIL) &
                    Q(message__emailmessage__headers__name__in=['To', 'From', 'CC', 'Delivered-To', 'Sender']) &
                    reduce(operator.or_, q_object_list)
                )
            )
        else:
            history_list = HistoryListItem.objects.filter(
                (Q(note__content_type=note_content_type_id) & Q(note__object_id=self.object.pk))
            )

        epoch = self.request.GET.get('datetime', None)
        if epoch:
            # Append datetime filter to the query
            try:
                filter_date = datetime.datetime.fromtimestamp(int(epoch))
                history_list = history_list.filter(sort_by_date__lt=filter_date)
            except ValueError:
                pass

        history_list = history_list.distinct().order_by('-sort_by_date')[:self.page_size]

        if self.is_ajax:
            context['list'] = history_list
            context['list_item_template'] = self.list_item_template
        else:
            context['history_list'] = history_list

        return context

    def is_valid_offset(self, offset):
        """
        Check the validity of the offset given in the GET parameters.

        :param offset: the offset set in the GET parameters
        :return: True or False, depending on the validity of offset
        """
        try:
            offset = int(offset)
        except ValueError:
            return False

        if not offset % self.page_size == 0:
            return False
        if offset < self.page_size:
            return False

        return True


delete_note_view = login_required(DeleteNoteView.as_view())
edit_note_view = login_required(EditNoteView.as_view())
