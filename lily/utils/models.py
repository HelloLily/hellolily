from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel

from lily.utils.functions import get_tenant_mixin as TenantMixin


# ISO 3166-1 country names and codes
#   adapted from http://opencountrycodes.appspot.com/python/
#   source from http://djangosnippets.org/snippets/1476/
COUNTRIES = (
    ('', _('Select a country')),
    ('NL', _('Netherlands')),
    ('BE', _('Belgium')),
    ('DE', _('Germany')),
    ('GB', _('United Kingdom')),
    ('US', _('United States')),
    ('AF', _('Afghanistan')),
    ('AX', _('Aland Islands')),
    ('AL', _('Albania')),
    ('DZ', _('Algeria')),
    ('AS', _('American Samoa')),
    ('AD', _('Andorra')),
    ('AO', _('Angola')),
    ('AI', _('Anguilla')),
    ('AQ', _('Antarctica')),
    ('AG', _('Antigua and Barbuda')),
    ('AR', _('Argentina')),
    ('AM', _('Armenia')),
    ('AW', _('Aruba')),
    ('AU', _('Australia')),
    ('AT', _('Austria')),
    ('AZ', _('Azerbaijan')),
    ('BS', _('Bahamas')),
    ('BH', _('Bahrain')),
    ('BD', _('Bangladesh')),
    ('BB', _('Barbados')),
    ('BY', _('Belarus')),
    ('BE', _('Belgium')),
    ('BZ', _('Belize')),
    ('BJ', _('Benin')),
    ('BM', _('Bermuda')),
    ('BT', _('Bhutan')),
    ('BO', _('Bolivia')),
    ('BA', _('Bosnia and Herzegovina')),
    ('BW', _('Botswana')),
    ('BV', _('Bouvet Island')),
    ('BR', _('Brazil')),
    ('IO', _('British Indian Ocean Territory')),
    ('BN', _('Brunei Darussalam')),
    ('BG', _('Bulgaria')),
    ('BF', _('Burkina Faso')),
    ('BI', _('Burundi')),
    ('KH', _('Cambodia')),
    ('CM', _('Cameroon')),
    ('CA', _('Canada')),
    ('CV', _('Cape Verde')),
    ('KY', _('Cayman Islands')),
    ('CF', _('Central African Republic')),
    ('TD', _('Chad')),
    ('CL', _('Chile')),
    ('CN', _('China')),
    ('CX', _('Christmas Island')),
    ('CC', _('Cocos (Keeling) Islands')),
    ('CO', _('Colombia')),
    ('KM', _('Comoros')),
    ('CG', _('Congo')),
    ('CD', _('Congo, The Democratic Republic of the')),
    ('CK', _('Cook Islands')),
    ('CR', _('Costa Rica')),
    ('CI', _('Cote d\'Ivoire')),
    ('HR', _('Croatia')),
    ('CU', _('Cuba')),
    ('CY', _('Cyprus')),
    ('CZ', _('Czech Republic')),
    ('DK', _('Denmark')),
    ('DJ', _('Djibouti')),
    ('DM', _('Dominica')),
    ('DO', _('Dominican Republic')),
    ('EC', _('Ecuador')),
    ('EG', _('Egypt')),
    ('SV', _('El Salvador')),
    ('GQ', _('Equatorial Guinea')),
    ('ER', _('Eritrea')),
    ('EE', _('Estonia')),
    ('ET', _('Ethiopia')),
    ('FK', _('Falkland Islands (Malvinas)')),
    ('FO', _('Faroe Islands')),
    ('FJ', _('Fiji')),
    ('FI', _('Finland')),
    ('FR', _('France')),
    ('GF', _('French Guiana')),
    ('PF', _('French Polynesia')),
    ('TF', _('French Southern Territories')),
    ('GA', _('Gabon')),
    ('GM', _('Gambia')),
    ('GE', _('Georgia')),
    ('DE', _('Germany')),
    ('GH', _('Ghana')),
    ('GI', _('Gibraltar')),
    ('GR', _('Greece')),
    ('GL', _('Greenland')),
    ('GD', _('Grenada')),
    ('GP', _('Guadeloupe')),
    ('GU', _('Guam')),
    ('GT', _('Guatemala')),
    ('GG', _('Guernsey')),
    ('GN', _('Guinea')),
    ('GW', _('Guinea-Bissau')),
    ('GY', _('Guyana')),
    ('HT', _('Haiti')),
    ('HM', _('Heard Island and McDonald Islands')),
    ('VA', _('Holy See (Vatican City State)')),
    ('HN', _('Honduras')),
    ('HK', _('Hong Kong')),
    ('HU', _('Hungary')),
    ('IS', _('Iceland')),
    ('IN', _('India')),
    ('ID', _('Indonesia')),
    ('IR', _('Iran, Islamic Republic of')),
    ('IQ', _('Iraq')),
    ('IE', _('Ireland')),
    ('IM', _('Isle of Man')),
    ('IL', _('Israel')),
    ('IT', _('Italy')),
    ('JM', _('Jamaica')),
    ('JP', _('Japan')),
    ('JE', _('Jersey')),
    ('JO', _('Jordan')),
    ('KZ', _('Kazakhstan')),
    ('KE', _('Kenya')),
    ('KI', _('Kiribati')),
    ('KP', _('Korea, Democratic People\'s Republic of')),
    ('KR', _('Korea, Republic of')),
    ('KW', _('Kuwait')),
    ('KG', _('Kyrgyzstan')),
    ('LA', _('Lao People\'s Democratic Republic')),
    ('LV', _('Latvia')),
    ('LB', _('Lebanon')),
    ('LS', _('Lesotho')),
    ('LR', _('Liberia')),
    ('LY', _('Libyan Arab Jamahiriya')),
    ('LI', _('Liechtenstein')),
    ('LT', _('Lithuania')),
    ('LU', _('Luxembourg')),
    ('MO', _('Macao')),
    ('MK', _('Macedonia, The Former Yugoslav Republic of')),
    ('MG', _('Madagascar')),
    ('MW', _('Malawi')),
    ('MY', _('Malaysia')),
    ('MV', _('Maldives')),
    ('ML', _('Mali')),
    ('MT', _('Malta')),
    ('MH', _('Marshall Islands')),
    ('MQ', _('Martinique')),
    ('MR', _('Mauritania')),
    ('MU', _('Mauritius')),
    ('YT', _('Mayotte')),
    ('MX', _('Mexico')),
    ('FM', _('Micronesia, Federated States of')),
    ('MD', _('Moldova')),
    ('MC', _('Monaco')),
    ('MN', _('Mongolia')),
    ('ME', _('Montenegro')),
    ('MS', _('Montserrat')),
    ('MA', _('Morocco')),
    ('MZ', _('Mozambique')),
    ('MM', _('Myanmar')),
    ('NA', _('Namibia')),
    ('NR', _('Nauru')),
    ('NP', _('Nepal')),
    ('NL', _('Netherlands')),
    ('AN', _('Netherlands Antilles')),
    ('NC', _('New Caledonia')),
    ('NZ', _('New Zealand')),
    ('NI', _('Nicaragua')),
    ('NE', _('Niger')),
    ('NG', _('Nigeria')),
    ('NU', _('Niue')),
    ('NF', _('Norfolk Island')),
    ('MP', _('Northern Mariana Islands')),
    ('NO', _('Norway')),
    ('OM', _('Oman')),
    ('PK', _('Pakistan')),
    ('PW', _('Palau')),
    ('PS', _('Palestinian Territory, Occupied')),
    ('PA', _('Panama')),
    ('PG', _('Papua New Guinea')),
    ('PY', _('Paraguay')),
    ('PE', _('Peru')),
    ('PH', _('Philippines')),
    ('PN', _('Pitcairn')),
    ('PL', _('Poland')),
    ('PT', _('Portugal')),
    ('PR', _('Puerto Rico')),
    ('QA', _('Qatar')),
    ('RE', _('Reunion')),
    ('RO', _('Romania')),
    ('RU', _('Russian Federation')),
    ('RW', _('Rwanda')),
    ('BL', _('Saint Barthelemy')),
    ('SH', _('Saint Helena')),
    ('KN', _('Saint Kitts and Nevis')),
    ('LC', _('Saint Lucia')),
    ('MF', _('Saint Martin')),
    ('PM', _('Saint Pierre and Miquelon')),
    ('VC', _('Saint Vincent and the Grenadines')),
    ('WS', _('Samoa')),
    ('SM', _('San Marino')),
    ('ST', _('Sao Tome and Principe')),
    ('SA', _('Saudi Arabia')),
    ('SN', _('Senegal')),
    ('RS', _('Serbia')),
    ('SC', _('Seychelles')),
    ('SL', _('Sierra Leone')),
    ('SG', _('Singapore')),
    ('SK', _('Slovakia')),
    ('SI', _('Slovenia')),
    ('SB', _('Solomon Islands')),
    ('SO', _('Somalia')),
    ('ZA', _('South Africa')),
    ('GS', _('South Georgia and the South Sandwich Islands')),
    ('ES', _('Spain')),
    ('LK', _('Sri Lanka')),
    ('SD', _('Sudan')),
    ('SR', _('Suriname')),
    ('SJ', _('Svalbard and Jan Mayen')),
    ('SZ', _('Swaziland')),
    ('SE', _('Sweden')),
    ('CH', _('Switzerland')),
    ('SY', _('Syrian Arab Republic')),
    ('TW', _('Taiwan, Province of China')),
    ('TJ', _('Tajikistan')),
    ('TZ', _('Tanzania, United Republic of')),
    ('TH', _('Thailand')),
    ('TL', _('Timor-Leste')),
    ('TG', _('Togo')),
    ('TK', _('Tokelau')),
    ('TO', _('Tonga')),
    ('TT', _('Trinidad and Tobago')),
    ('TN', _('Tunisia')),
    ('TR', _('Turkey')),
    ('TM', _('Turkmenistan')),
    ('TC', _('Turks and Caicos Islands')),
    ('TV', _('Tuvalu')),
    ('UG', _('Uganda')),
    ('UA', _('Ukraine')),
    ('AE', _('United Arab Emirates')),
    ('GB', _('United Kingdom')),
    ('US', _('United States')),
    ('UM', _('United States Minor Outlying Islands')),
    ('UY', _('Uruguay')),
    ('UZ', _('Uzbekistan')),
    ('VU', _('Vanuatu')),
    ('VE', _('Venezuela')),
    ('VN', _('Viet Nam')),
    ('VG', _('Virgin Islands, British')),
    ('VI', _('Virgin Islands, U.S.')),
    ('WF', _('Wallis and Futuna')),
    ('EH', _('Western Sahara')),
    ('YE', _('Yemen')),
    ('ZM', _('Zambia')),
    ('ZW', _('Zimbabwe')),
)


class Deleted(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    deleted = ModificationDateTimeField(_('deleted'))
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PhoneNumber(TenantMixin):
    """
    Phone number model, keeps a raw input version and a clean version (only has digits).
    """
    # TODO: check possibilities for integration of
    # - http://pypi.python.org/pypi/phonenumbers and/or
    # - https://github.com/stefanfoulis/django-phonenumber-field

    PHONE_TYPE_CHOICES = (
        ('work', _('Work')),
        ('mobile', _('Mobile')),
        ('other', _('Other')),
    )

    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    PHONE_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )

    raw_input = models.CharField(max_length=40, verbose_name=_('phone number'))
    number = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=PHONE_TYPE_CHOICES, default='work',
                            verbose_name=_('type'))
    other_type = models.CharField(max_length=15, blank=True, null=True) # used in combination with type='other'
    status = models.IntegerField(max_length=10, choices=PHONE_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))

    def __unicode__(self):
        return self.number

    def save(self, *args, **kwargs):
        # Save raw input as number only (for searching)
        self.number = filter(type(self.raw_input).isdigit, self.raw_input)
        
        # Replace starting digits
        if self.number[:3] == '310':
            self.number = self.number.replace('310', '31', 1)
        if self.number[:2] == '06':
            self.number = self.number.replace('06', '316', 1)
        if self.number[:1] == '0':
            self.number = self.number.replace('0', '31', 1)
        
        if len(self.number) > 0:
            self.number = '+' + self.number
        
            # Overwrite user input
            self.raw_input = self.number # reserved field for future display based on locale
        
        return super(PhoneNumber, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('phone number')
        verbose_name_plural = _('phone numbers')


class SocialMedia(TenantMixin):
    """
    Social media model, default supporting a few well known social media but has support for
    custom input (other_name).
    """
    SOCIAL_NAME_CHOICES = (
        ('facebook', _('Facebook')),
        ('twitter', _('Twitter')),
        ('linkedin', _('LinkedIn')),
        ('googleplus', _('Google+')),
        ('qzone', _('Qzone')),
        ('orkut', _('Orkut')),
        ('other', _('Other')),
    )

    name = models.CharField(max_length=30,choices=SOCIAL_NAME_CHOICES, verbose_name=_('name'))
    other_name = models.CharField(max_length=30, blank=True, null=True) # used in combination with name='other'
    username = models.CharField(max_length=100, blank=True, verbose_name=_('username'))
    profile_url = models.URLField(verbose_name=_('profile link'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('social media')
        verbose_name_plural = _('social media')


class Address(TenantMixin):
    """
    Address model, has most default fields for an address and fixed preset values for type. In
    the view layer options are limited for different models. For example: options for an address
    for an account excludes 'home' as options for an address for a contact exclude 'visiting'.
    """
    ADDRESS_TYPE_CHOICES = (
        ('visiting', _('Visiting address')),
        ('billing', _('Billing address')),
        ('shipping', _('Shipping address')),
        ('home', _('Home address')),
        ('other', _('Other')),
    )

    street = models.CharField(max_length=255, verbose_name=_('street'), blank=True)
    street_number = models.SmallIntegerField(verbose_name=_('street number'), blank=True, null=True)
    complement = models.CharField(max_length=10, verbose_name=_('complement'), blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('postal code'), blank=True)
    city = models.CharField(max_length=100, verbose_name=_('city'), blank=True)
    state_province = models.CharField(max_length=50, verbose_name=_('state/province'), blank=True)
    # TODO: maybe try setting a default based on account/user preferences for country
    country = models.CharField(max_length=2, choices=COUNTRIES, verbose_name=_('country'), blank=True)
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, verbose_name=_('type'))

    def __unicode__(self):
        return u'%s %s %s' % (self.street or '', self.street_number or '', self.complement or '')

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class EmailAddress(TenantMixin):
    """
    Email address model, it's possible to set an email address as primary address as a model can
    own multiple email addresses.
    """
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    EMAIL_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )

    email_address = models.EmailField(max_length=255, verbose_name=_('e-mail address'))
    is_primary = models.BooleanField(default=False, verbose_name=_('primary e-mail'))
    status = models.IntegerField(max_length=50, choices=EMAIL_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))

    def __unicode__(self):
        return self.email_address

    class Meta:
        verbose_name = _('e-mail address')
        verbose_name_plural = _('e-mail addresses')


class Common(Deleted, TenantMixin):
    """
    Common model to make it possible to easily define relations to other models.
    """
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True,
                                           verbose_name=_('list of phone numbers'))
    social_media = models.ManyToManyField(SocialMedia, blank=True,
                                          verbose_name=_('list of social media'))
    addresses = models.ManyToManyField(Address, blank=True,
                                       verbose_name=_('list of addresses'))
    email_addresses = models.ManyToManyField(EmailAddress, blank=True,
                                             verbose_name=_('list of e-mail addresses'))
    notes = generic.GenericRelation('notes.Note', content_type_field='content_type',
                                    object_id_field='object_id', verbose_name='list of notes')

    class Meta:
        abstract = True
