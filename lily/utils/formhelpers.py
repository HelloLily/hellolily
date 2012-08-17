from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, LayoutSlice
from django.utils.translation import ugettext as _

from lily.utils.templatetags.utils import has_user_in_group


class LilyFormHelper(FormHelper):
    """
    Simple FormHelper with extra functionality to simply replace a field in a layout to prevent
    redefining it completely.
    """
    def __init__(self, form=None):
        super(LilyFormHelper, self).__init__(form=form)
        # change the default to inline
        self.form_style = 'inline'
    
    def replace(self, field_name, field):
        """
        Helper method to replace default generated layout for fields, for a custom one.
        """
        field_index = self.layout.fields.index(field_name)
        self.layout.pop(field_index)
        self.layout.insert(field_index, field)
    
    def exclude_by_widgets(self, widget_types):
        """
        Returns a LayoutSlice pointing to fields with widgets not like `widget_types`
        """
        assert(self.layout is not None and self.form is not None)
        layout_field_names = self.layout.get_field_names()
        
        retrieve_index = lambda L: isinstance(L, list) and retrieve_index(L[0]) or not isinstance(L, list) and L
        retrieve_name = lambda L: isinstance(L[0], list) and len(L[0]) > 1 and retrieve_name(L[0]) or isinstance(L[0], list) and L[1]

        # Let's filter all fields with widgets not like widget_types
        filtered_fields = []
        if len(layout_field_names) > 1 and type(layout_field_names[1]) is str:
            i = 0
            while i < len(layout_field_names):
                try:
                    index = layout_field_names[i][0]
                    name = layout_field_names[i+1]
                    field = self.form.fields[name]
                    if not type(field.widget) in widget_types:
                        filtered_fields.append(index)
                except:
                    pass
                i += 2
        else:
            for pointer in layout_field_names:
                try:
                    name = retrieve_name(pointer)
                    _index = retrieve_index(pointer)
                    index = int(_index) if not type(_index) is int else _index
                    field = self.form.fields[name]
                    if not type(field.widget) in widget_types:
                        filtered_fields.append(index)
                except:
                    pass
        return LayoutSlice(self.layout, filtered_fields)

class DeleteBackAddSaveFormHelper(LilyFormHelper):
    """
    Provide three buttons: 
        delete (conditional)
        back
        add or save
    """
    def __init__(self, form=None):
        super(DeleteBackAddSaveFormHelper, self).__init__(form=form)
        
        if form.instance.pk is not None:
            if not has_user_in_group(form.instance, 'account_admin'):
                self.add_input(Submit('delete', _('Delete'), 
                   css_id='delete-%s' % form.instance.pk, 
                   css_class='link delete %s red float-left' % form.instance.__class__.__name__.lower())
                )
        
        self.add_input(Submit('submit-back', _('Back'), css_class='red'))
        if form.instance.pk is not None: 
            self.add_input(Submit('submit-save', _('Save')))
        else:
            self.add_input(Submit('submit-add', _('Add')))
