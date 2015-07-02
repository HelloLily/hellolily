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
        for item_data in data.pop(field['data_string']):
            if not item_data['is_deleted']:
                # Remove is_deleted key so the create doesn't raise an error
                del item_data['is_deleted']

                # Websites are different than the other related fields
                # For now just have it as an edge case in this function
                # In the future we might want to change how websites are setup
                if field['model'] == 'Website':
                    model = get_model('accounts', field['model'])
                    model.objects.create(account=instance, **item_data)
                else:
                    # Get the model
                    model = get_model('utils', field['model'])
                    # Create new object from model and add to set
                    getattr(instance, field['data_string']).add(model.objects.create(**item_data))


def update_related_fields(instance, related_fields, data):
    """
    Function used to create/update/delete the related fields when updating an existing object.

    Args:
        instance (object): The object whose related fields are going to be created
        related_fields (dict): Dict containing information about the related fields
        data (dict): Dict containing the actual data for the related fields
    """
    for field in related_fields:
        for item_data in data.pop(field['data_string']):
            if not item_data:
                continue

            # Convert from OrderedDict to regular dict
            item_data_dict = dict(item_data)
            is_deleted = item_data_dict['is_deleted']

            # Remove is_deleted key from dict (so update/create don't give errors)
            del item_data_dict['is_deleted']

            if 'id' in item_data_dict:
                # ID is set, so the object exists. Get that object
                # Note that this isn't a single object but a QuerySet
                # This is because passing a dict to the .update only works on a QuerySet
                item_obj = getattr(instance, field['data_string']).filter(pk=item_data_dict['id'])

                # If the related field was marked as deleted, delete it
                if is_deleted:
                    item_obj.delete()
                else:
                    # Otherwise update the object
                    item_obj.update(**item_data_dict)
            else:
                # ID wasn't given, so:
                # 1. Get the model
                # 2. Get the related field set
                # 3. Create an new object from the model and add it to the set

                # Websites are different than the other related fields
                # For now just have it as an edge case in this function
                # In the future we might want to change how websites are setup
                if field['model'] == 'Website':
                    model = get_model('accounts', field['model'])

                    # Websites aren't added to a set, but are given an account
                    item_data_dict.update({
                        'account': instance
                    })
                    model.objects.create(**item_data_dict)
                else:
                    model = get_model('utils', field['model'])
                    getattr(instance, field['data_string']).add(model.objects.create(**item_data_dict))
