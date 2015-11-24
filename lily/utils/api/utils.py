from django.db.models.loading import get_model


def create_related_fields(instance, related_fields, data):
    """
    Function used to create the related fields when creating a new object.

    Args:
        instance (object): The object whose related fields are going to be created
        related_fields (dict): Dict containing information about the related fields
        data (dict): Dict containing the actual data for the related fields
    """
    for field in related_fields:
        for item_data in data.get(field['data_string']):
            # Remove is_deleted key from dict (so update/create don't give errors)
            is_deleted = item_data.pop('is_deleted', False)

            if item_data and not is_deleted:
                # Websites are different than the other related fields.
                # For now just have it as an edge case in this function.
                # In the future we might want to change how websites are setup.
                if field['model'] == 'Website':
                    model = get_model('accounts', field['model'])
                    model.objects.create(account=instance, **item_data)
                else:
                    # Get the model
                    if field['model'] == 'SocialMedia':
                        model = get_model('socialmedia', field['model'])
                    else:
                        model = get_model('utils', field['model'])
                    # Create new object from model and add to set
                    field_name = field['data_string']
                    getattr(instance, field_name).add(model.objects.create(**item_data))


def update_related_fields(instance, related_fields, data):
    """
    Function used to create/update/delete the related fields when updating an existing object.

    Args:
        instance (object): The object whose related fields are going to be created/updated/deleted
        related_fields (dict): Dict containing information about the related fields
        data (dict): Dict containing the actual data for the related fields
    """
    for field in related_fields:
        # Pop items here so setattr() works
        for item_data in data.pop(field['data_string'], {}):
            # In case something went wrong in the front end and an object with
            # the is_deleted flag wasn't removed we set the object to an empty dict.
            # So just to be sure we check for empty data.
            if not item_data:
                continue

            # Convert from OrderedDict to regular dict
            item_data = dict(item_data)

            # Remove is_deleted key from dict (so update/create don't give errors)
            is_deleted = item_data.pop('is_deleted', False)

            if 'id' in item_data:
                # ID is set, so the object exists. Get that object.
                # Note that this isn't a single object but a QuerySet.
                # This is because passing a dict to the .update only works on a QuerySet.
                field_name = field['data_string']
                item_obj = getattr(instance, field_name).filter(pk=item_data['id'])

                # If the related field was marked as deleted, delete it
                if is_deleted:
                    item_obj.delete()
                else:
                    # TODO: Temporary fix to strip slashes
                    if field['model'] == 'Website':
                        item_data['website'] = item_data['website'].strip('/')

                    # Otherwise update the object
                    item_obj.update(**item_data)
            else:
                # ID wasn't given, so:
                # 1. Get the model
                # 2. Get the related field set
                # 3. Create an new object from the model and add it to the set

                # Websites are different than the other related fields.
                # For now just have it as an edge case in this function.
                # In the future we might want to change how websites are setup.
                if field['model'] == 'Website':
                    model = get_model('accounts', field['model'])

                    # Websites aren't added to a set, but are given an account
                    item_data.update({
                        'account': instance
                    })
                    model.objects.create(**item_data)
                elif field['model'] == 'SocialMedia':
                    model = get_model('socialmedia', field['model'])
                    field_name = field['data_string']

                    manager = getattr(instance, field_name)
                    manager.exclude(id=instance.id).delete()
                    getattr(instance, field_name).add(model.objects.create(**item_data))
                else:
                    model = get_model('utils', field['model'])
                    field_name = field['data_string']
                    getattr(instance, field_name).add(model.objects.create(**item_data))
