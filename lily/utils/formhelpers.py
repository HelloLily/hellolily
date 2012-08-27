from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, LayoutSlice
from django.utils.translation import ugettext as _

from lily.utils.layout import MultiField, InlineRow, ColumnedRow, Row
from lily.utils.templatetags.utils import has_user_in_group


class LilyFormHelper(FormHelper):
    """
    Simple FormHelper with extra functionality to simply replace a field in a layout to prevent
    redefining it completely.
    """
    def __init__(self, form=None):
        super(LilyFormHelper, self).__init__(form=form)
        # set the default to inline
        self.form_style = 'inline'
    
    def wrap_by_names(self, layoutObject, *field_names):
        """
        Wrap fields *field_names within layoutObject.
        
        Example:
        self.helper.wrap_by_names(Row, 'description', 'tags')
        """
        layout_field_names = self.layout.get_field_names()
        for pointer in layout_field_names:
            pos = pointer[0]
            layout_object = self.layout.fields[pos[0]]
            for i in pointer[0][1:-1]:
                layout_object = layout_object.fields[i]
            
            # If layout object has no fields attribute, then it's a basestring (a field name)
            if not hasattr(layout_object, 'fields'):
                if layout_object in field_names:
                    self.layout.fields[pos[0]] = layoutObject(layout_object)
            else:
                if layout_object.fields[pos[-1]] in field_names:
                    layout_object.fields[pos[-1]] = layoutObject(layout_object.fields[pos[-1]])
    
    def get_field_name_in_object(self, layoutObject):
        """
        Get the field_name from a field wrapped inside a layoutObject.
        """
        if isinstance(layoutObject, list):
            return self.get_field_name_in_object(layoutObject[0])
        else:
            if isinstance(layoutObject[0], basestring):
                return layoutObject[0]
            
        return None
    
    def delete_label_for(self, *field_names):
        """
        Remove the label for given fields.
        """
        for field_name in field_names:
            if field_name in self.form.fields:
                self.form.fields[field_name].label = ''
    
    def create_only_columns(self, *columns):
        """
        Create a layoutObject which contains given columns.
        """
        return ColumnedRow(*columns)
    
    def create_columns(self, *columns, **kwargs):
        """
        Create a MultiField which contains given columns. 
        """
        label = kwargs.pop('label', self.form.fields[self.get_field_name_in_object(columns[0])].label)
        inline = kwargs.pop('inline', False)
        if inline:
            layout =  MultiField(
                label,
                self.create_only_columns(*columns)
            )
        else: 
            layout =  Row(
                MultiField(
                    label,
                    InlineRow(self.create_only_columns(*columns)),
                )
            )
        
        for column in columns:
            field_name = self.get_field_name_in_object(column)
            if field_name is not None:
                self.delete_label_for(field_name)
                
        return layout
    
    def add_columns(self, *columns, **kwargs):
        """
        Append given columns to the current layout using a MultiField layout.
        """
        self.layout.append(
            self.create_columns(*columns, **kwargs)
        )
        
    def create_large_field(self, field_name, **kwargs):
        """
        Create a simple layout for a field that expands to the width of the container (form).
        """
        label = kwargs.pop('label', self.form.fields[field_name].label)
        layout = Row(
            MultiField(
                label,
                InlineRow(field_name),
            )
        )
        
        return layout
    
    def add_large_field(self, field_name, **kwargs):
        """
        Append given field to the current layout using a MultiField layout.
        """
        self.layout.append(
            self.create_large_field(field_name, **kwargs)
        )
        
        self.delete_label_for(field_name)
    
    def add_large_fields(self, *field_names, **kwargs):
        """
        Append multiple fields to the current layout using a MultiField layout.
        """
        for field_name in field_names:
            self.add_large_field(field_name)
    
    def create_multi_row(self, *rows, **kwargs):
        """
        Create a MultiField which contains multiple rows with columns inside.
        
        Example:
        self.helper.layout.insert(0, 
            self.helper.create_multi_row(
                (
                    Column('salutation', size=2, first=True),
                    Column('gender', size=2),
                ),
                (
                    Column('first_name', size=3, first=True),
                    Column('preposition', size=1),
                    Column('last_name', size=4),
                ),
                label=_('Name'),
            )
        )
        """
        label = kwargs.pop('label', self.form.fields[rows[0][0][0]].label)
        layout = Row(
            MultiField(
                label,
                *[InlineRow(self.create_only_columns(*row)) for row in rows]
            )
        )
        
        for row in rows:
            for column in row:
                field_name = self.get_field_name_in_object(column)
                if field_name is not None:
                    self.delete_label_for(field_name)
        
        return layout
    
    def add_multi_row(self, *rows, **kwargs):
        """
        Append a multiple rows using a MultiField layout.
        """
        self.layout.append(
            self.create_multi_row(*rows, **kwargs)
        )
    
    def replace(self, field_name, field):
        """
        Replace default generated layout for fields, for a custom one.
        
        Example:
        self.helper.replace('account',
            self.helper.create_columns(
                Column('account', size=4, first=True)
            ),
        )
        """
        field_index = self.layout.fields.index(field_name)
        self.layout.pop(field_index)
        self.layout.insert(field_index, field)
        
        self.delete_label_for('note')


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
