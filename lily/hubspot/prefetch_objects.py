from django.db.models import Prefetch, Case, When, Value, IntegerField, Q

from lily.accounts.models import Website, Account
from lily.integrations.models import Document
from lily.notes.models import Note
from lily.socialmedia.models import SocialMedia
from lily.tags.models import Tag
from lily.utils.models.models import Address, PhoneNumber, EmailAddress

website_prefetch = Prefetch(
    lookup='websites',
    queryset=Website.objects.exclude(Q(website='http://') | Q(website='https://')).order_by('-is_primary').all(),
    to_attr='prefetched_websites'
)

addresses_prefetch = Prefetch(
    lookup='addresses',
    queryset=Address.objects.all(),
    to_attr='prefetched_addresses'
)

phone_prefetch = Prefetch(
    lookup='phone_numbers',
    queryset=PhoneNumber.objects.filter(
        status=PhoneNumber.ACTIVE_STATUS
    ).annotate(
        custom_order=Case(
            When(type='work', then=Value(1)),
            When(type='mobile', then=Value(2)),
            When(type='home', then=Value(3)),
            When(type='other', then=Value(4)),
            When(type='fax', then=Value(5)),
            output_field=IntegerField(),
        )
    ).order_by('custom_order'),
    to_attr='prefetched_phone_numbers'
)

social_media_prefetch = Prefetch(
    lookup='social_media',
    queryset=SocialMedia.objects.all(),
    to_attr='prefetched_social_media'
)

notes_prefetch = Prefetch(
    lookup='notes',
    queryset=Note.objects.all(),
    to_attr='prefetched_notes'
)

tags_prefetch = Prefetch(
    lookup='tags',
    queryset=Tag.objects.all(),
    to_attr='prefetched_tags'
)

accounts_prefetch = Prefetch(
    lookup='accounts',
    queryset=Account.objects.filter(is_deleted=False),
    to_attr='prefetched_accounts'
)

email_addresses_prefetch = Prefetch(
    lookup='email_addresses',
    queryset=EmailAddress.objects.exclude(status=EmailAddress.INACTIVE_STATUS).order_by('-status'),
    to_attr='prefetched_email_addresses'
)

twitter_prefetch = Prefetch(
    lookup='social_media',
    queryset=SocialMedia.objects.filter(name='twitter'),
    to_attr='prefetched_twitters'
)

document_prefetch = Prefetch(
    lookup='document_set',
    queryset=Document.objects.all(),
    to_attr='prefetched_documents'
)
