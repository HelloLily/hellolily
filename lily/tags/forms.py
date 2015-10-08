from django.contrib.contenttypes.models import ContentType
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _

from lily.utils.forms import HelloLilyModelForm
from lily.utils.forms.fields import TagsField
from lily.utils.forms.widgets import ShowHideWidget, TagInput

from .models import Tag


class TagsFormMixin(HelloLilyModelForm):
    """
    Mixin that adds tags to a ModelForm.
    """
    tags = TagsField(required=False, widget=ShowHideWidget(TagInput()))

    def __init__(self, *args, **kwargs):
        super(TagsFormMixin, self).__init__(*args, **kwargs)

        # Provide autocomplete suggestions and already linked tags
        self.fields['tags'].initial = ','.join(
            str(tag) for tag in self.instance.tags.all().values_list('name', flat=True))
        self.fields['tags'].choices = list(Tag.objects.filter(
            content_type=ContentType.objects.get_for_model(self.instance.__class__)
        ).values_list('name', flat=True).distinct())

        if hasattr(self.fieldsets, 'fieldsets') and isinstance(self.fieldsets.fieldsets, tuple):
            # Only automatically add a tags field if it's not set on one of the
            # current form fieldsets yet.
            tags_in_form = False

            for fieldsets in self.fieldsets.fieldsets:
                for fieldset in fieldsets:
                    if 'fields' in fieldset and 'tags' in fieldset['fields']:
                        tags_in_form = True

            if not tags_in_form:
                self.fieldsets.fieldsets = self.fieldsets.fieldsets + (
                    (_('Tags'), {'fields': ('tags',), }),
                )

    def save(self, commit=True):
        """
        Overloading super().save to create save tags and create the
        relationships with this account instance. Needs to be done here because
        the Tags are expected to exist before self.instance is saved.
        """
        # Get the tags and remove them from cleaned_data first, so the parent
        # modelform won't complain when saving.
        cased_tags = self.cleaned_data.get('tags')
        tags = map(lambda x: x.lower(), cased_tags)
        del self.cleaned_data['tags']
        instance = super(TagsFormMixin, self).save()

        for tag in tags:
            # Create relationship with Tag if it's a new tag.
            tag_object, created = Tag.objects.get_or_create(
                name=tag,
                object_id=getattr(instance, instance.__class__._meta.pk.column),
                content_type=ContentType.objects.get_for_model(instance.__class__),
            )
            if created:
                instance.tags.add(tag_object)

        # Remove tags with any relationships to instance that weren't
        # included in POST data.
        tags_to_remove = Tag.objects.filter(~Q(name__in=tags), object_id=instance.pk)
        tags_to_remove.delete()

        return instance

    class Meta:
        fields = ('tags',)
