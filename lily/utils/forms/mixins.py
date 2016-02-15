class FormSetFormMixin(object):
    """
    Custom form mixin to allow easier use of formset fields.

    With the setup of the formset fields the formset_form_attrs
    kwargs is translated to form_attrs on the specific fields.

    Also there is custom save logic for each of the formset fields.
    """
    def __init__(self, *args, **kwargs):
        """
        Custom init function to set the form_attrs on each formset field specified in formset_form_attrs.

        Args:
            formset_form_attrs (dict, optional): Dict specifying the fields and value for the form_attr of that field.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        The formset_form_attrs argument is a dict with the following structure:
            formset_form_attrs = {
                'formset_field_name': {
                    'attr1': ['value', ],
                    'attr2': {},
                }
            }
        """
        formset_form_attrs = kwargs.pop('formset_form_attrs', {})
        super(FormSetFormMixin, self).__init__(*args, **kwargs)

        if formset_form_attrs is not None:
            for key, value in formset_form_attrs.items():
                self.fields[key].form_attrs = value

    def save(self, commit=True):
        """
        Custom save to call the save function on formset fields declared on this form

        Because form fields declared on the form do not have a save that is automatically called on form save,
        a loop is required to call the custom save logic of each of the formset fields. This only applies to
        fields declared on the form (not model fields etc.) with the is_formset attribute set to True.

        Args:
            commit (boolean, optional): Specify whether to actually save or just return the instance.

        Returns:
            Instance: Newly saved if commit is True otherwise the instance received by super call.
        """
        instance = super(FormSetFormMixin, self).save(commit)

        # If commit call the custom save of all newly declared formset fields
        if commit:
            # Loop through declared fields because only fields declared on the form need custom saving
            for name, field in self.declared_fields.items():
                # Check if the field is a formset field, by checking if the is_formset attribute is set
                if hasattr(field, 'is_formset'):
                    field.save(instance, self.cleaned_data.get(name), name)

        return instance
