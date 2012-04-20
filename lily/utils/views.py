from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.encoding import smart_str
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin


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


class DetailFormView(FormMixin, SingleObjectMixin, TemplateResponseMixin, View):
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
                
        context = self.get_context_data(object=self.object, form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = kwargs
        
        context_object_name = self.get_context_object_name(self.object)
        if context_object_name:
            context[context_object_name] = self.object
        
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(object=self.object, form=form))