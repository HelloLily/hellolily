import json
import grequests

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from rest_framework import serializers

from lily.api.mixins import ValidateEverythingSimultaneouslyMixin
from lily.tags.models import Tag


class WritableNestedSerializer(ValidateEverythingSimultaneouslyMixin, serializers.ModelSerializer):
    """
    Generic implementation of saving related fields.

    Just put a related field serializer amongst the normal fields
    """
    def _separate_data(self, validated_data):
        many_related_data = {}
        fk_related_data = {}
        generic_related_data = {}

        # Warning: model meta class api changes in django 1.9 so these lists need to be rewritten.
        # See https://docs.djangoproject.com/en/1.9/ref/models/meta/#migrating-from-the-old-api
        fk_fields = [f.name for f in self.Meta.model._meta.local_fields if isinstance(f, models.ForeignKey)]
        generic_fk_fields = [field.name for field in self.Meta.model._meta.virtual_fields]
        many_to_many_fields = [field.name for field in self.Meta.model._meta.many_to_many]

        for field_name in validated_data.copy():  # Copy because a dict can't be modified during loop.
            # Check for many to many fields.
            if field_name in many_to_many_fields:
                many_related_data[field_name] = validated_data.pop('%s' % field_name)
                # Go to next field, because this one was recognized.
                continue

            # Check for foreign key fields.
            if field_name in fk_fields:
                fk_related_data[field_name] = validated_data.pop('%s' % field_name)
                # Go to next field, because this one was recognized.
                continue

            # Check for generic relation fields.
            if field_name in generic_fk_fields:
                generic_related_data[field_name] = validated_data.pop('%s' % field_name)

        return validated_data, many_related_data, fk_related_data, generic_related_data

    def create(self, validated_data):
        original_validated_data = validated_data.copy()

        # Prepare all data for saving.
        (non_related_data, many_related_data,
         fk_related_data, generic_related_data) = self._separate_data(validated_data)

        with transaction.atomic():
            # Do save of foreign key related fields.
            for field_name, field_data in fk_related_data.items():
                pk = field_data.get('id')
                serializer = self.fields[field_name]

                if pk:
                    related_instance = serializer.Meta.model.objects.get(pk=pk)

                    # Update the related instance with new data if necessary.
                    if not len(field_data) == 1:
                        related_instance = serializer.update(related_instance, field_data)
                else:
                    related_instance = serializer.create(field_data)

                # Add the id's so null constraints don't break.
                non_related_data.update({
                    '%s_id' % field_name: related_instance.pk,
                })

            instance = super(WritableNestedSerializer, self).create(non_related_data)

            # Do save of generic related fields.
            for field_name, field_data in generic_related_data.items():
                serializer = self.fields[field_name]

                # Add the reference to the current object in the field data.
                for item in field_data:
                    content_type = ContentType.objects.get_for_model(instance)
                    item.update({
                        'content_type': content_type,
                        'object_id': instance.pk,
                    })

                serializer.create(field_data)

            # Do save of many to many related fields.
            for field_name, field_data in many_related_data.items():
                serializer = self.fields[field_name]
                related_instance_list = serializer.create([fd for fd in field_data if not fd.get('id')])
                related_instance_list += serializer.update(instance, [fd for fd in field_data if fd.get('id')])

                getattr(instance, field_name).add(*related_instance_list)

            self.call_webhook(original_validated_data, instance)

        return instance

    def update(self, instance, validated_data):
        original_validated_data = validated_data.copy()

        # Prepare all data for saving.
        (non_related_data, many_related_data,
         fk_related_data, generic_related_data) = self._separate_data(validated_data)

        if self.partial:
            for related_field_name in many_related_data:
                # Store which fields are removed to update many_related_data afterwards.
                removed_ids = []
                # The non-model field is_deleted isn't present in many_related_data, so use initial_data instead.
                field_data = self.initial_data[related_field_name]
                for item in field_data:
                    if 'is_deleted' in item and item['is_deleted']:
                        getattr(self.instance, related_field_name).filter(id=item['id']).delete()
                        removed_ids.append(item['id'])

                # Update many_related_data without the removed items.
                # Keep items without an id, those will be newly created items.
                many_related_data[related_field_name] = [
                    item for item in many_related_data[related_field_name]
                    if 'id' not in item or not item['id'] in removed_ids
                ]

            # Compare the current tags with the submitted tags to determine which tags should be deleted.
            # Handle tags as a special case, because removed tags have no is_deleted flag,
            # in fact they aren't present in initial_data at all.
            if 'tags' in generic_related_data:
                current_tag_ids = [tag['id'] for tag in instance.tags.all().values()]
                submitted_existing_tag_ids = [tag['id'] for tag in generic_related_data['tags'] if 'id' in tag]
                removed_tag_ids = set(current_tag_ids) ^ set(submitted_existing_tag_ids)
                if len(removed_tag_ids):
                    Tag.objects.filter(id__in=removed_tag_ids).delete()

        with transaction.atomic():
            instance = super(WritableNestedSerializer, self).update(instance, non_related_data)

            # Do save of many to many related fields.
            for field_name, field_data in many_related_data.items():
                serializer = self.fields[field_name]
                related_instance_list = serializer.update(None, field_data)
                manager = getattr(instance, field_name)

                if not self.root.partial:
                    # It's a full update, so we replace all currently linked objects with the new objects.
                    manager.remove(*manager.exclude(id__in=[obj.id for obj in related_instance_list]))

                manager.add(*related_instance_list)

            # Do save of foreign key related fields.
            for field_name, field_data in fk_related_data.items():
                if not field_data:
                    # Field data was null, so unset the relation.
                    setattr(instance, field_name, None)
                else:
                    pk = field_data.get('id')

                    if pk:
                        if pk == getattr(instance, '%s_id' % field_name):
                            # We don't change the related instance.
                            # Get the related instance to work with.
                            related_instance = getattr(instance, field_name)
                        else:
                            # Change the related instance.
                            # Get the new related instance to work with.
                            related_instance = getattr(self.Meta.model, field_name).get_queryset().get(pk=pk)
                            # Set the new related instance as linked to this instance.
                            setattr(instance, field_name, related_instance)

                        # Update the related instance with new data if necessary.
                        if not len(field_data) == 1:
                            serializer = self.fields[field_name]
                            serializer.update(related_instance, field_data)
                    else:
                        serializer = self.fields[field_name]
                        related_instance = serializer.create(field_data)
                        # Set the new related instance as linked to this instance.
                        setattr(instance, field_name, related_instance)

                instance.save()

            # Do save of generic related fields
            for field_name, field_data in generic_related_data.items():
                # Add the reference to the current object in the field data.
                for item in field_data:
                    item.update({
                        'subject': instance,
                    })

                serializer = self.fields[field_name]
                related_instance_list = serializer.update(None, field_data)
                manager = getattr(instance, field_name)

                if not self.root.partial:
                    # It's a full update, so we replace all currently linked objects with the new objects.
                    manager.exclude(id__in=[obj.id for obj in related_instance_list]).delete()

            self.call_webhook(original_validated_data)

        return instance

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
                }
            else:
                data = {
                    'type': model,
                    'data': original_validated_data,
                    'object': self.data,
                }

            data = json.dumps(data, sort_keys=True, default=lambda x: str(x))

            webhook_calls = (grequests.post(wh.url, data=data) for wh in [webhook])

            try:
                # User has a webhook set, so post the data to the given URL.
                grequests.map(webhook_calls)
            except:
                pass


class WritableNestedListSerializer(serializers.ListSerializer):
    """
    List serializer that can be used to enable nested updates
    """

    def update(self, instance, validated_data):
        instance_list = []

        for attrs in validated_data:
            pk = attrs.pop('id', None)

            if pk:
                instance = self.child.Meta.model.objects.get(pk=pk)
                obj = self.child.update(instance, attrs)
            else:
                obj = self.child.create(attrs)

            instance_list.append(obj)

        return instance_list
