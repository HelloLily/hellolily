from oauth2client.contrib.django_orm import Storage as BaseStorage


class Storage(BaseStorage):
    def locked_put(self, credentials, overwrite=False):
        """
        Override the save, so it uses updated_fields.
        Otherwise null constraints start complaining.
        """
        args = {self.key_name: self.key_value}

        if overwrite:
            entity, unused_is_new = self.model_class.objects.get_or_create(**args)
        else:
            entity = self.model_class(**args)

        setattr(entity, self.property_name, credentials)
        entity.save(updated_fields=[self.property_name, ])
