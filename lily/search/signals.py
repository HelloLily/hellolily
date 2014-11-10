import itertools

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver

from lily.search.indexing import get_class, update_in_index, remove_from_index
from lily.socialmedia.models import SocialMedia
from lily.tags.models import Tag
from lily.utils.models.models import PhoneNumber, Address, EmailAddress


CLASS_MAPPINGS = [get_class(kls) for kls in settings.ES_MODEL_MAPPINGS]
MODEL_TO_MAPPING = {kls.get_model(): kls for kls in CLASS_MAPPINGS}

RELATED = set(itertools.chain(*[kls.get_related_models() for kls in CLASS_MAPPINGS]))
TYPE_SETS = [kls.get_type_set() for kls in CLASS_MAPPINGS]

COMMON_TYPES = [PhoneNumber, SocialMedia, Address, EmailAddress]
GENERIC_FOREIGN_TYPES = [Tag]


@receiver(post_save)
def post_save_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        update_in_index(instance, mapping)
    # Check for related model signals.
    check_related(sender, instance)


@receiver(post_delete)
def post_delete_generic(sender, instance, **kwargs):
    mapping = MODEL_TO_MAPPING.get(sender)
    if mapping:
        remove_from_index(instance, mapping)
    # Remember: We UPDATE our related object, not DELETE it
    # (So we can use the check_related also used in the post_save method).
    check_related(sender, instance)


def check_related(sender, instance):
    if sender in RELATED:
        if sender in COMMON_TYPES:
            # A Common type, we need to check the corresponding set.
            # (Note is not supported for now).
            for type_set in TYPE_SETS:
                objects_set = getattr(instance, type_set)
                if objects_set:
                    for obj in objects_set.all():
                        mapping = MODEL_TO_MAPPING.get(obj.__class__)
                        if mapping:
                            if sender in mapping.get_related_models():
                                update_in_index(obj, mapping)
        elif sender in GENERIC_FOREIGN_TYPES:
            # A generic foreign key. Check if it points to our mapping instances.
            subject = instance.subject
            mapping = MODEL_TO_MAPPING.get(subject.__class__)
            if mapping:
                if sender in mapping.get_related_models():
                    update_in_index(subject, mapping)
        else:
            # Check fields that have the right type.
            for field_name in [field.name for field in sender._meta.concrete_fields]:
                kls = getattr(instance, field_name).__class__
                mapping = MODEL_TO_MAPPING.get(kls)
                if mapping:
                    if sender in mapping.get_related_models():
                        update_in_index(getattr(instance, field_name), mapping)
