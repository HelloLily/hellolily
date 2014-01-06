from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q

from lily.tags.models import Tag
from lily.utils.fields import TagsField


class TagsFormMixin(forms.ModelForm):
    """
    Mixin that adds tags to a ModelForm.
    """
    tags = TagsField(required=False)

    def __init__(self, *args, **kwargs):
        super(TagsFormMixin, self).__init__(*args, **kwargs)

        # Provide autocomplete suggestions and already linked tags
        self.fields['tags'].initial = ','.join(str(tag) for tag in self.instance.tags.all().values_list('name', flat=True))
        self.fields['tags'].choices = list(Tag.objects.filter(content_type=ContentType.objects.get_for_model(self.instance.__class__)).values_list('name', flat=True).distinct())

    def save(self, commit=True):
        """
        Overloading super().save to create save tags and create the relationships with
        this account instance. Needs to be done here because the Tags are expected to exist
        before self.instance is saved.
        """
        # Save model instance
        instance = super(TagsFormMixin, self).save()

        # Save tags
        tags = self.cleaned_data.get('tags')

        for tag in tags:
            # Create relationship with Tag if it's a new tag
            tag_object, created = Tag.objects.get_or_create(
                name=tag,
                object_id=getattr(instance, instance.__class__._meta.pk.column),
                content_type=ContentType.objects.get_for_model(instance.__class__),
            )
            if created:
                instance.tags.add(tag_object)

        # Remove tags with any relationships to instance that weren't included in POST data
        tags_to_remove = Tag.objects.filter(~Q(name__in=tags), object_id=instance.pk)
        tags_to_remove.delete()

        return instance

    class Meta:
        fields = ('tags',)
