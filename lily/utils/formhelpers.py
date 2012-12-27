import collections
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.translation import ugettext as _

from lily.utils.layout import MultiField, InlineRow, ColumnedRow, Row
from lily.utils.templatetags.utils import has_user_in_group


class LilyFormHelper(FormHelper):
    """
    Simple FormHelper with extra functionality to simply replace a field in a layout to prevent
    redefining it completely.
    """
    form_tag = False

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

    def insert_before(self, layoutObject, *field_names):
        """
        Insert layoutObject before all field_names in the layout.

        Example:
        self.helper.insert_before(Divider(), 'field_3', 'field6')
        """
        for field_name in field_names:
            layout_field_names = reversed(self.layout.get_field_names())
            for pointer in layout_field_names:
                pointer_field_name, index = self.get_field_name_from_pointer(pointer)
                if field_name == pointer_field_name:
                    # Insert before field_name
                    field_index = index
                    self.layout.insert(field_index, layoutObject)

    def insert_after(self, layoutObject, *field_names):
        """
        Insert layoutObject after all field_names in the layout.
        
        Example:
        self.helper.insert_after(Divider(), 'field_3', 'field6')
        """
        for field_name in field_names:
            layout_field_names = self.layout.get_field_names()
            for pointer in layout_field_names:
                pointer_field_name, index = self.get_field_name_from_pointer(pointer)
                if field_name == pointer_field_name:
                    # Insert after field_name
                    field_index = index + 1
                    self.layout.insert(field_index, layoutObject)

    def get_field_name_from_pointer(self, pointer):
        """
        Return  the field_name and index for this field from a pointer.
        """
        pos = pointer[0]
        layout_object = self.layout.fields[pos[0]]
        for i in pointer[0][1:-1]:
            if hasattr(layout_object, 'fields'):
                layout_object = layout_object.fields[i]
                
        # If layout object has no fields attribute, then it's a basestring (a field name)
        if not hasattr(layout_object, 'fields'):
            return layout_object, pos[0]
        else:
            return layout_object.fields[pos[-1]], pos[0]

    def get_field_name_from_layout(self, layout_object):
        """
        Get the first field_name wrapped inside one or more layout_objects.
        """
        if hasattr(layout_object, 'fields'):
            for field in layout_object.fields:
                if isinstance(field, basestring):
                    return field
        elif isinstance(layout_object, collections.Iterable):
            for object in layout_object:
                field_name = self.get_field_name_from_layout(object)
                if isinstance(field_name, basestring):
                    return field_name
        
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
        if 'label' in kwargs:
            label = kwargs['label']
        else:
            label = self.form.fields[self.get_field_name_from_layout(columns)].label

        if 'inline' in kwargs:
            inline = kwargs['inline']
        else:
            inline = False

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
            field_name = self.get_field_name_from_layout(column)
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
        inline = kwargs.pop('inline', False)
        if inline:
            layout = MultiField(
                label,
                InlineRow(field_name),
            )
        else:
            layout = Row(
                MultiField(
                    label,
                    InlineRow(field_name),
                )
            )
        
        self.delete_label_for(field_name)
        
        return layout
    
    def add_large_field(self, field_name, **kwargs):
        """
        Append given field to the current layout using a MultiField layout.
        """
        self.layout.append(
            self.create_large_field(field_name, **kwargs)
        )
    
    def add_large_fields(self, *field_names, **kwargs):
        """
        Append multiple fields to the current layout using a MultiField layout.
        """
        for field_name in field_names:
            self.add_large_field(field_name, **kwargs)
    
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
                field_name = self.get_field_name_from_layout(column)
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
    
    def replace(self, field, layoutObject):
        """
        Replace default generated layout for field, for a custom one.
        
        Example:
        self.helper.replace('account',
            self.helper.create_columns(
                Column('account', size=4, first=True)
            ),
        )
        """
        layout_field_names = self.layout.get_field_names()
        for pointer in layout_field_names:
            field_name, index = self.get_field_name_from_pointer(pointer)
            if field_name == field:
                self.layout.pop(index)
                self.layout.insert(index, layoutObject)
                
                self.delete_label_for(field_name)

    def replace_fields(self, field_dict, layoutObject, size):
        for name in field_dict:
            self.replace(name,
                self.create_columns(
                    layoutObject(name, size=size, first=True), label=field_dict.get(name, '')
                )
            )

    def remove(self, *fields):
        """
        Remove fields from global layout.
        """
        layout_field_names = self.layout.get_field_names()
        for pointer in reversed(layout_field_names):
            field_name, index = self.get_field_name_from_pointer(pointer)
            if field_name in fields:
                self.layout.pop(index)


class DeleteBackAddSaveFormHelper(LilyFormHelper):
    """
    Provide three buttons: 
        delete (conditional)
        back
        add or save
    """
    def __init__(self, form=None):
        super(DeleteBackAddSaveFormHelper, self).__init__(form=form)
        
        if hasattr(form, 'instance') and form.instance.pk is not None:
            if not has_user_in_group(form.instance, 'account_admin'):
                self.add_input(Submit('delete', _('Delete'), 
                   css_id='delete-%s' % form.instance.pk, 
                   css_class='link delete %s red float-left' % form.instance.__class__.__name__.lower())
                )
        
        self.add_input(Submit('submit-back', _('Back'), css_class='red'))
        if hasattr(form, 'instance') and form.instance.pk is not None:
            self.add_input(Submit('submit-save', _('Save')))
        else:
            self.add_input(Submit('submit-add', _('Add')))