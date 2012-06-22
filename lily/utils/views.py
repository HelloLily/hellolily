import types

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.http import Http404, HttpResponse
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.http import base36_to_int
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin

from lily.utils.forms import NoteForm


class CustomSingleObjectMixin(object):
    """
    Namespace the variables so this mixin can be combined with other 
    mixins which also use model/queryset. Behaviour besides this is 
    the same as default Django SingleObjectMixin.
    """
    detail_model = None
    detail_queryset = None
    detail_slug_field = 'slug'
    detail_context_object_name = None
    detail_slug_url_kwarg = 'slug'
    detail_pk_url_kwarg = 'pk'
    
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.detail_queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        # Use a custom detail_queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_detail_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.detail_pk_url_kwarg, None)
        slug = self.kwargs.get(self.detail_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_detail_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object pk or a slug."
                                 % self.__class__.__name__)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_(u"No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.detail_model._meta.verbose_name})
        return obj

    def get_detail_queryset(self):
        """
        Get the detail_queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        if self.detail_queryset is None:
            if self.detail_model:
                return self.detail_model._default_manager.all()
            else:
                raise ImproperlyConfigured(u"%(cls)s is missing a detail_queryset. Define "
                                           u"%(cls)s.detail_model, %(cls)s.detail_queryset, or override "
                                           u"%(cls)s.get_object()." % {
                                                'cls': self.__class__.__name__
                                        })
        return self.detail_queryset._clone()

    def get_detail_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.detail_slug_field

    def get_detail_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.detail_context_object_name:
            return self.detail_context_object_name
        elif hasattr(obj, '_meta'):
            return smart_str(obj._meta.object_name.lower())
        else:
            return None


class CustomMultipleObjectMixin(object):
    """
    Namespace the variables so this mixin can be combined with other 
    mixins which also use model/queryset. Behaviour besides this is 
    the same as default Django MultipleObjectMixin.
    """
    allow_empty = True
    list_queryset = None
    list_model = None
    paginate_by = None
    list_context_object_name = None
    paginator_class = Paginator

    def get_list_queryset(self):
        """
        Get the list of items for this view. This must be an interable, and may
        be a list_queryset (in which qs-specific behavior will be enabled).
        """
        if self.list_queryset is not None:
            queryset = self.list_queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.list_model is not None:
            queryset = self.list_model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'list_queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the list_queryset, if needed.
        """
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404(_(u"Page is not 'last', nor can it be converted to an int."))
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404(_(u'Invalid page (%(page_number)s)') % {
                                'page_number': page_number
            })

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return self.paginate_by

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        Return an instance of the paginator for this view.
        """
        return self.paginator_class(queryset, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)

    def get_allow_empty(self):
        """
        Returns ``True`` if the view should display empty lists, and ``False``
        if a 404 should be raised instead.
        """
        return self.allow_empty

    def get_list_context_object_name(self, object_list):
        """
        Get the name of the item to be used in the context.
        """
        if self.list_context_object_name:
            return self.list_context_object_name
        elif hasattr(object_list, 'model'):
            return smart_str('%s_list' % object_list.model._meta.object_name.lower())
        else:
            return None


class DetailListFormView(FormMixin, CustomSingleObjectMixin, CustomMultipleObjectMixin, TemplateResponseMixin, View):
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        allow_empty = self.get_allow_empty()
        
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        
        context = self.get_context_data(object=self.object, form=form, object_list=self.object_list)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = self.get_list_queryset()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = kwargs
        
        detail_context_object_name = self.get_detail_context_object_name(self.object)
        if detail_context_object_name:
            context[detail_context_object_name] = self.object
        
        queryset = kwargs.pop('object_list')
        page_size = self.get_paginate_by(queryset)
        list_context_object_name = self.get_list_context_object_name(queryset)
        
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context.update({
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            })
        else:
            context.update({
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            })
            
        if list_context_object_name is not None:
            context[list_context_object_name] = queryset
        
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form, object_list=self.object_list))


class DetailNoteFormView(FormMixin, SingleObjectMixin, TemplateResponseMixin, View):
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

        return super(DetailNoteFormView, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form))

    def get_success_url(self):
        if not hasattr(self, 'success_url_reverse_name'):
            return super(DetailNoteFormView, self).get_success_url()
        
        return reverse(self.success_url_reverse_name, kwargs={ 'pk': self.object.pk })


class MultipleModelListView(TemplateView):
    """
    Class for showing multiple lists of models in a template.
    """
    models = [] # Either a list of models or a dictionary
    object_lists = {} # dictionary with all objects lists
    context_name_suffix = '_list' # suffix for the context available in the template
    
    def dispatch(self, request, *args, **kwargs):
        """
        Overloading super().dispatch to query for object lists first.
        """
        self.get_objects_lists()
        
        return super(MultipleModelListView, self).dispatch(request, *args, **kwargs)
    
    def get_objects_lists(self):
        """
        Retrieve the queryset for all models and save them in self.object_lists.
        """
        if type(self.models) == types.ListType:
            for model in self.models:
                list_name = smart_str(model._meta.object_name.lower())
                self.object_lists.update({
                    list_name: self.get_model_queryset(list_name, model)
                })
        elif type(self.models) == types.DictType:
            for list_name, model in self.models.items():
                self.object_lists.update({
                    list_name: self.get_model_queryset(list_name, model)
                })
    
    def get_model_queryset(self, list_name, model):
        """
        Return the queryset for given model.
        """
        return model._default_manager.all()
    
    def get_context_data(self, **kwargs):
        """
        Put all object lists into the context data.
        """
        kwargs = super(MultipleModelListView, self).get_context_data(**kwargs)
        for list_name, object_list in self.object_lists.items():
            if type(self.models) == types.ListType:
                list_name = '%s%s' % (list_name, self.context_name_suffix)
                    
            kwargs.update({
                list_name : object_list
            })
        return kwargs
    
    
class FilteredListMixin(object):
    """
    Mixin that enables filtering objects by url, based on their primary keys. 
    """
    
    def get_queryset(self):
        """
        Overriding super().get_queryset to limit the queryset based on a kwarg when provided.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if hasattr(queryset, '_clone'):
                queryset = queryset._clone()
        elif self.model is not None:
            # If kwarg is provided, try reducing the queryset
            if self.kwargs.get('b36_pks', None):
                try:
                    # Convert base36 to int
                    b36_pks = self.kwargs.get('b36_pks').split(';')
                    int_pks = []
                    for pk in b36_pks:
                        int_pks.append(base36_to_int(pk))
                    # Filter queryset
                    queryset = self.model._default_manager.filter(pk__in=int_pks)
                except:
                    queryset = self.model._default_manager.all()
            else:
                queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(u"'%s' must define 'queryset' or 'model'"
                                       % self.__class__.__name__)
        return queryset


class SortedListMixin(object):
    """
    Mixin that enables sorting ascending and descending on set columns.
    """
    ASC = 'asc'
    DESC = 'desc'
    sortable = [] # Columns that can be ordered
    default_sort_order = ASC # Direction to order in
    default_order_by = 1 # Column to order
    
    def __init__(self, *args, **kwargs):
        """
        Make sure default_order_by is in sortable or use the default regardless.
        """
        if hasattr(self, 'order_by') and self.order_by not in self.sortable:
            self.order_by = self.default_order_by 
    
    def get_context_data(self, **kwargs):
        """
        Add sorting information from instance variables or request.GET.
        """
        
        try:
            if int(self.request.GET.get('order_by')) in self.sortable:
                self.order_by = self.request.GET.get('order_by')
            else:
                if not hasattr(self, 'order_by'):
                    self.order_by = self.default_order_by        
        except:
            self.order_by = self.default_order_by
            
        if self.request.GET.get('sort_order') in [self.ASC, self.DESC]:
            self.sort_order = self.request.GET.get('sort_order')
        else:
            if not hasattr(self, 'sort_order'):
                self.sort_order = self.default_sort_order
            
        kwargs.update({
            'order_by': self.order_by,
            'sort_order': self.sort_order,
        })
        
        return kwargs


class AjaxUpdateView(View):
    """
    View that provides an option to update models based on a url and POST data.
    """
    http_method_names = ['post']
    
    def post(self, request, *args, **kwargs):
        try:
            app_name = kwargs.pop('app_name')
            model_name = kwargs.pop('model_name').lower().capitalize()
            object_id = kwargs.pop('object_id')
            
            model = get_model(app_name, model_name)
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
        return HttpResponse(simplejson.dumps({}), mimetype='application/json')


# Perform logic here instead of in urls.py
ajax_update_view = login_required(AjaxUpdateView.as_view())
    