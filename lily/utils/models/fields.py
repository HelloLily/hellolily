from django.conf import settings
from django.db.models import DateTimeField


class CreatedDateTimeField(DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['auto_now_add'] = True
        super(CreatedDateTimeField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"


class ModifiedDateTimeField(DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['auto_now'] = True
        super(ModifiedDateTimeField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "DateTimeField"

    def pre_save(self, model_instance, add):
        # If update_modified is set to false on the instance or if we're migrating, don't update the modified date.
        if not getattr(model_instance, 'update_modified', True) or settings.MIGRATING:
            return model_instance.modified
        return super(ModifiedDateTimeField, self).pre_save(model_instance, add)
