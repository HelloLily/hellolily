import json
import grequests

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import ForeignKey, ManyToManyField, ManyToOneRel, ManyToManyRel
from django.utils import six
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import SerializerMetaclass

from lily.api.mixins import ValidateEverythingSimultaneouslyMixin


def is_dirty(instance, data):
    """
    Helper function to determine whether a serializer needs to save.
    """
    if not instance:
        return True

    for key, value in data.items():
        if value != getattr(instance, key):
            return True

    return False


class WritableNestedSerializerMetaclass(SerializerMetaclass):
    def __new__(mcs, name, bases, attrs):
        cls = super(WritableNestedSerializerMetaclass, mcs).__new__(mcs, name, bases, attrs)

        if name != 'WritableNestedSerializer':
            cls.model_fields = {x.name: x for x in cls.Meta.model._meta.get_fields()}

            cls.simple_fields = []

            cls.foreign_key_fields = []
            cls.foreign_key_reverse_fields = []

            cls.generic_foreign_key_fields = []
            cls.generic_foreign_key_reverse_fields = []

            cls.many_to_many_fields = []
            cls.many_to_many_through_fields = []

            cls.many_to_many_reverse_fields = []
            cls.many_to_many_through_reverse_fields = []

            for field_name, field in cls.model_fields.items():
                if not field.is_relation:
                    # It's a normal field.
                    cls.simple_fields.append(field_name)
                    continue
                else:
                    # The field is some type of relation.
                    if isinstance(field, ForeignKey):
                        # The field is a foreign key.
                        cls.foreign_key_fields.append(field_name)
                        continue

                    if isinstance(field, ManyToOneRel):
                        # The field is a reverse foreign key.
                        cls.foreign_key_reverse_fields.append(field_name)
                        continue

                    if isinstance(field, GenericForeignKey):
                        # The field is a generic foreign key.
                        cls.generic_foreign_key_fields.append(field_name)
                        continue

                    if isinstance(field, GenericRelation):
                        # The field is a reverse generic foreign key.
                        cls.generic_foreign_key_reverse_fields.append(field_name)
                        continue

                    if isinstance(field, ManyToManyField):
                        # The field is a many to many.
                        if hasattr(field.rel.through, 'manager'):
                            # With a custom through table.
                            cls.many_to_many_through_fields.append(field_name)
                        else:
                            # Without a custom through table.
                            cls.many_to_many_fields.append(field_name)
                        continue

                    if isinstance(field, ManyToManyRel):
                        # The field is a reverse many to many.
                        if hasattr(field.through, 'manager'):
                            cls.many_to_many_through_reverse_fields.append(field_name)
                        else:
                            cls.many_to_many_reverse_fields.append(field_name)
                        continue

        return cls


@six.add_metaclass(WritableNestedSerializerMetaclass)
class WritableNestedSerializer(ValidateEverythingSimultaneouslyMixin, serializers.ModelSerializer):
    simple_data = {}
    fk_data = {}
    fk_reverse_data = {}
    gfk_data = {}
    gfk_reverse_data = {}
    m2m_data = {}
    m2m_reverse_data = {}
    m2m_through_data = {}
    m2m_through_reverse_data = {}

    def __init__(self, instance=None, data=empty, **kwargs):
        super(WritableNestedSerializer, self).__init__(instance=instance, data=data, **kwargs)

        # Set these here, because they're of mutable type. Inheritance uses the super data otherwise.
        self.simple_data = {}
        self.fk_data = {}
        self.fk_reverse_data = {}
        self.gfk_data = {}
        self.gfk_reverse_data = {}
        self.m2m_data = {}
        self.m2m_reverse_data = {}
        self.m2m_through_data = {}
        self.m2m_through_reverse_data = {}

    def split_data(self, data):
        for field_name, field_data in data.items():
            if field_name in self.foreign_key_fields:
                self.fk_data[field_name] = field_data
                continue

            if field_name in self.foreign_key_reverse_fields:
                self.fk_reverse_data[field_name] = field_data
                continue

            if field_name in self.generic_foreign_key_fields:
                self.gfk_data[field_name] = field_data
                continue

            if field_name in self.generic_foreign_key_reverse_fields:
                self.gfk_reverse_data[field_name] = field_data
                continue

            if field_name in self.many_to_many_fields:
                self.m2m_data[field_name] = field_data
                continue

            if field_name in self.many_to_many_reverse_fields:
                self.m2m_reverse_data[field_name] = field_data
                continue

            if field_name in self.many_to_many_through_fields:
                self.m2m_through_data[field_name] = field_data
                continue

            if field_name in self.many_to_many_through_reverse_fields:
                self.m2m_through_reverse_data[field_name] = field_data
                continue

            self.simple_data[field_name] = field_data

    def save(self, **kwargs):
        # Get the content type for the model of the current serializer.
        self.ctype = ContentType.objects.get_for_model(self.Meta.model)
        return super(WritableNestedSerializer, self).save(**kwargs)

    def create(self, validated_data):
        self.split_data(validated_data)

        with transaction.atomic():
            # Save the foreign keys and add their id's to simple field data.
            self.save_foreign_key_fields()

            # Save the instance using simple field data.
            self.instance = super(WritableNestedSerializer, self).create(self.simple_data)

            # Save the reverse foreign keys.
            self.save_foreign_key_reverse_fields()

            # Save the generic foreign keys.
            self.save_generic_foreign_key_fields()

            # Save the reverse generic foreign keys.
            self.save_generic_foreign_key_reverse_fields()

            # Save the many to manys.
            self.save_many_to_many_fields()

            # Save the reverse many to manys.
            self.save_many_to_many_reverse_fields()

            # Save the many to manys with a through model.
            self.save_many_to_many_through_fields()

            # Save the reverse many to manys with a through model.
            self.save_many_to_many_through_reverse_fields()

        self.call_webhook(validated_data, self.instance)

        return self.instance

    def update(self, instance, validated_data):
        self.split_data(validated_data)

        with transaction.atomic():
            # Save the foreign keys and add their id's to simple field data.
            self.save_foreign_key_fields()

            # Save the instance.
            self.instance = super(WritableNestedSerializer, self).update(instance, self.simple_data)

            # Save the reverse foreign keys and do a cleanup of unreferenced objects if necessary.
            self.save_foreign_key_reverse_fields(cleanup=True)

            # Save the generic foreign keys.
            self.save_generic_foreign_key_fields()

            # Save the reverse generic foreign keys.
            self.save_generic_foreign_key_reverse_fields(cleanup=True)

            # Save the many to manys.
            self.save_many_to_many_fields(cleanup=True)

            # Save the reverse many to manys.
            self.save_many_to_many_reverse_fields(cleanup=True)

            # Save the many to manys with a through model.
            self.save_many_to_many_through_fields(cleanup=True)

            # Save the reverse many to manys with a through model.
            self.save_many_to_many_through_reverse_fields(cleanup=True)

        self.call_webhook(validated_data, self.instance)

        return self.instance

    def remove(self, unmentioned_instances, field_name, manager, many):
        # Store which fields are removed to update related_data afterwards.
        removed_ids = []

        if self.root.partial:
            for item in self.initial_data.get(field_name, []):
                if 'is_deleted' in item and item['is_deleted']:
                    removed_ids.append(item['id'])
        else:
            removed_ids = unmentioned_instances.keys()

        # Delete the instances which were marked for deletion.
        if many:
            manager.remove(*manager.filter(pk__in=removed_ids))
        else:
            manager.filter(pk__in=removed_ids).delete()

    def save_foreign_key_fields(self):
        for field_name, field_data in self.fk_data.items():
            related_instance = self.fields[field_name].instance

            if related_instance:
                if is_dirty(related_instance, field_data):
                    # Something has changed, save the related object.
                    related_instance = self.fields[field_name].save()

                # Add the id's so null constraints don't break.
                self.simple_data['%s_id' % field_name] = related_instance.pk
            elif field_data:
                self.simple_data['%s_id' % field_name] = field_data['id']
            else:
                self.simple_data['%s_id' % field_name] = None

    def save_foreign_key_reverse_fields(self, cleanup=False):
        for field_name, field_data in self.fk_reverse_data.items():
            # Get the manager object for the reverse fk relation.
            manager = self.fields[field_name].child.Meta.model.objects
            # Get the related name for this foreign key.
            related_name = '%s_id' % self.model_fields[field_name].field.name
            # Update the field data with a reference to the instance.
            for obj in field_data:
                obj[related_name] = self.instance.pk

            # Call the save on the listserializer.
            instance_list, unmentioned_instances = self.fields[field_name].save(self.instance, field_data)

            if cleanup:
                self.remove(unmentioned_instances, field_name, manager, False)

    def save_generic_foreign_key_fields(self):
        if self.gfk_data:
            raise NotImplementedError('generic_foreign_key_fields are not supported yet.')

    def save_generic_foreign_key_reverse_fields(self, cleanup=False):
        for field_name, field_data in self.gfk_reverse_data.items():
            # Get the manager object for the reverse gfk relation.
            manager = self.fields[field_name].child.Meta.model.objects
            # Update the field data with the generic fk information (object_id and ctype).
            for obj in field_data:
                obj[self.model_fields[field_name].object_id_field_name] = self.instance.pk
                obj[self.model_fields[field_name].content_type_field_name] = self.ctype

            instance_list, unmentioned_instances = self.fields[field_name].save(self.instance, field_data)

            if cleanup:
                self.remove(unmentioned_instances, field_name, manager, False)

    def save_many_to_many_fields(self, cleanup=False):
        for field_name, field_data in self.m2m_data.items():
            # Get the manager object for the m2m relation.
            manager = getattr(self.instance, field_name)
            # Call the save on the listserializer.
            instance_list, unmentioned_instances = self.fields[field_name].save(self.instance, field_data)
            # Add the many to many relation.
            manager.add(*instance_list)

            if cleanup:
                self.remove(unmentioned_instances, field_name, manager, True)

    def save_many_to_many_reverse_fields(self, cleanup=False):
        for field_name, field_data in self.m2m_reverse_data.items():
            # Get the manager object for the m2m relation.
            manager = getattr(self.instance, field_name)
            # Call the save on the listserializer.
            instance_list, unmentioned_instances = self.fields[field_name].save(self.instance, field_data)
            # Add the many to many relation.
            manager.add(*instance_list)

            if cleanup:
                self.remove(unmentioned_instances, field_name, manager, True)

    def save_many_to_many_through_fields(self, cleanup=False):
        for field_name, field_data in self.m2m_through_data.items():
            # Call the save on the listserializer.
            instance_list, unmentioned_instances = self.fields[field_name].save(self.instance, field_data)

            model_cls = self.model_fields[field_name].rel.through
            forward_field_name = self.model_fields[field_name].rel.field.m2m_field_name()
            reverse_field_name = self.model_fields[field_name].rel.field.m2m_reverse_field_name()

            for obj in instance_list:
                # Create the objects through records.
                data = {}
                data[forward_field_name] = self.instance
                data[reverse_field_name] = obj

                model_cls.objects.get_or_create(**data)

            if cleanup:
                removed_ids = []
                if self.root.partial:
                    for item in self.initial_data[field_name]:
                        if not isinstance(item, int) and 'is_deleted' in item and item['is_deleted']:
                            removed_ids.append(item['id'])
                else:
                    removed_ids = unmentioned_instances.keys()

                # Delete the instances which were not in the validated data.
                filter_kwargs = {
                    forward_field_name: self.instance,
                    '%s_id__in' % reverse_field_name: removed_ids,
                }

                model_cls.objects.filter(**filter_kwargs).delete()

    def save_many_to_many_through_reverse_fields(self, cleanup=False):
        if self.m2m_through_reverse_data:
            raise NotImplementedError('many_to_many_through_reverse_fields are not supported yet.')

    def call_webhook(self, original_validated_data, instance=None):
        user = self.context.get('request').user
        # Get the webhook of the user.
        webhook = user.webhooks.first()
        # For now we only want to send a POST request for the following events.
        events = ['account', 'case', 'contact', 'deal']
        # Get the class name of the instance.
        model = self.Meta.model._meta.model_name

        if webhook and model in events:
            if instance:
                # Create, so we don't have the instance ID available in the data.
                original_validated_data.update({
                    'id': instance.id,
                })

                data = {
                    'type': model,
                    'data': original_validated_data,
                    'object': self.data,
                    'event': 'create',
                }
            else:
                data = {
                    'type': model,
                    'data': original_validated_data,
                    'object': self.data,
                    'event': 'update',
                }

            data = json.dumps(data, sort_keys=True, default=lambda x: str(x))

            headers = {
                'Content-Type': 'application/json',
            }

            webhook_calls = (grequests.post(wh.url, data=data, headers=headers) for wh in [webhook])

            try:
                # User has a webhook set, so post the data to the given URL.
                grequests.map(webhook_calls)
            except:
                pass


class WritableNestedListSerializer(serializers.ListSerializer):
    """
    List serializer that can be used to enable nested updates
    """

    def save(self, instance, validated_data):
        saved_instances = []

        field = getattr(instance, self.source)
        instance_list = {obj.pk: obj for obj in field.all()}
        assign_list = {}

        # Loop over all the objects in validated_data.
        for obj in validated_data:
            pk = obj.get('id')

            if pk:
                if pk in instance_list:
                    # The validated data reference an existing object.
                    instance = instance_list.pop(pk)
                    if is_dirty(instance, obj):
                        saved_instances.append(self.update(instance, obj))
                else:
                    # This is an assignment. the pk isn't in the list of referenced instances for this endpoint.
                    assign_list[pk] = obj
            else:
                # The validated data are trying to create a new object.
                saved_instances.append(self.create(obj))

        saved_instances += self.assign(assign_list)

        return saved_instances, instance_list

    def create(self, validated_data):
        return self.child.create(validated_data)

    def update(self, instance, validated_data):
        return self.child.update(instance, validated_data)

    def assign(self, validated_data):
        saved_instances = []

        if validated_data:
            instance_list = {obj.pk: obj for obj in self.child.Meta.model.objects.filter(pk__in=list(validated_data))}

            for pk, data in validated_data.items():
                saved_instances.append(self.update(instance_list[pk], data))

        return saved_instances
