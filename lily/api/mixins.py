import json

from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from lily.changes.models import Change
from lily.socialmedia.models import SocialMedia
from lily.timelogs.models import TimeLog
from lily.timelogs.api.serializers import TimeLogSerializer
from lily.utils.functions import format_phone_number


class ModelChangesMixin(object):
    def create(self, request, *args, **kwargs):
        response = super(ModelChangesMixin, self).create(request, *args, **kwargs)

        obj_id = response.data.get('id')
        content_type_id = response.data.get('content_type').get('id')
        content_type = ContentType.objects.get(pk=content_type_id)

        Change.objects.create(
            action='post',
            data=json.dumps(request.data),
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
        )

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        action = 'patch' if partial else 'put'
        ignored_fields = ['modified', 'id', 'full_name']

        # Store the old data so we can compare changes.
        serializer = self.get_serializer(instance=self.get_object())
        old_data = serializer.data

        response = super(ModelChangesMixin, self).update(request, *args, **kwargs)

        obj = self.get_object()
        serializer = self.get_serializer(instance=obj)
        new_data = serializer.data

        # Social media fields are saved in a 'special' way.
        # Since we want to show changes per social media type we split all the data.
        if 'social_media' in request.data:
            for item in old_data.get('social_media'):
                social_type = item.get('name')

                if social_type not in old_data:
                    old_data[social_type] = []

                old_data[social_type].append(item)

            del old_data['social_media']

            for item in new_data.get('social_media'):
                social_type = item.get('name')

                if social_type not in new_data:
                    new_data[social_type] = []

                new_data[social_type].append(item)

            del new_data['social_media']

            for key in dict(SocialMedia.SOCIAL_NAME_CHOICES).keys():
                if key in old_data and key not in new_data:
                    new_data[key] = []
                elif key in new_data and key not in old_data:
                    old_data[key] = []

        data = {}
        # Compare old and new data and store those keys.
        diffkeys = [k for k in old_data if old_data.get(k) != new_data.get(k)]

        for key in diffkeys:
            is_social_media = (key in dict(SocialMedia.SOCIAL_NAME_CHOICES).keys())

            if key in request.data or is_social_media:
                # We don't want to display an ID in the change log,
                # so fetch the display name if possible.
                choice_field_name = key + '_display'

                if choice_field_name in old_data:
                    old = old_data.get(choice_field_name)
                else:
                    old = old_data.get(key)

                if isinstance(old, dict):
                    if 'name' in old:
                        old = old.get('name')
                    elif 'full_name' in old:
                        old = old.get('full_name')

                if choice_field_name in new_data:
                    new = new_data.get(choice_field_name)
                else:
                    new = new_data.get(key)

                if isinstance(new, dict):
                    if 'name' in new:
                        new = new.get('name')
                    elif 'full_name' in new:
                        new = new.get('full_name')

                # Related fields (e.g. phone numbers) are always lists.
                if is_social_media or isinstance(request.data[key], list):
                    if len(old) > len(new):
                        for item in old:
                            # If the item has been deleted we still want to register the change.
                            if not any(x.get('id') == item.get('id') for x in new):
                                new.append({
                                    'id': item.get('id'),
                                    'is_deleted': True,
                                })

                change = {
                    key: {
                        'old': old,
                        'new': new,
                    }
                }

                data.update(change)

        # Remove keys we don't want to track.
        for key in data.keys():
            if key in ignored_fields:
                del data[key]

        Change.objects.create(
            action=action,
            data=json.dumps(data),
            user=request.user,
            content_type=obj.content_type,
            object_id=obj.id,
        )

        return response

    @detail_route(methods=['get'])
    def changes(self, request, pk=None):
        obj = self.get_object()

        change_objects = Change.objects.filter(object_id=obj.id, content_type=obj.content_type)
        changes = []

        for change in change_objects:
            user = {
                'id': change.user.id,
                'full_name': change.user.full_name,
                'profile_picture': change.user.profile_picture,
            }

            changes.append({
                'id': change.id,
                'action': change.action,
                'data': json.loads(change.data),
                'user': user,
                'created': change.created,
            })

        return Response({'objects': changes})


class TimeLogMixin(object):
    @detail_route(methods=['get'])
    def timelogs(self, request, pk=None):
        obj = self.get_object()

        timelogs = TimeLog.objects.filter(gfk_object_id=obj.id, gfk_content_type=obj.content_type)

        serializer = TimeLogSerializer(timelogs, many=True)

        return Response({'objects': serializer.data})


class PhoneNumberFormatMixin(object):
    def get_country(self, instance):
        country = None

        if instance.addresses.exists():
            country = instance.addresses.first().country

        if not country:
            country = instance.tenant.country

        return country

    def create(self, validated_data):
        instance = super(PhoneNumberFormatMixin, self).create(validated_data)

        phone_numbers = instance.phone_numbers.all()

        if phone_numbers:
            country = self.get_country(instance)

            if country:
                for phone in phone_numbers:
                    phone.number = format_phone_number(phone.number, country, True)
                    phone.save()

        return instance

    def update(self, instance, validated_data):
        instance = super(PhoneNumberFormatMixin, self).update(instance, validated_data)

        phone_numbers = instance.phone_numbers.all()

        if phone_numbers:
            country = self.get_country(instance)

            if country:
                for phone in phone_numbers:
                    phone.number = format_phone_number(phone.number, country, True)
                    phone.save()

        return instance


class DataExistsMixin(object):
    @list_route(methods=['GET'])
    def exists(self, request):
        """
        Return if there is any data.
        """
        exists = self.get_queryset().exists()
        return Response(exists)
