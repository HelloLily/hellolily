# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=255, verbose_name='street', blank=True)),
                ('street_number', models.SmallIntegerField(null=True, verbose_name='street number', blank=True)),
                ('complement', models.CharField(max_length=255, null=True, verbose_name='complement', blank=True)),
                ('postal_code', models.CharField(max_length=10, verbose_name='postal code', blank=True)),
                ('city', models.CharField(max_length=100, verbose_name='city', blank=True)),
                ('state_province', models.CharField(max_length=50, verbose_name='state/province', blank=True)),
                ('country', models.CharField(blank=True, max_length=2, verbose_name='country', choices=[(b'', 'Select a country'), (b'NL', 'Netherlands'), (b'BE', 'Belgium'), (b'DE', 'Germany'), (b'GB', 'United Kingdom'), (b'US', 'United States'), (b'AF', 'Afghanistan'), (b'AX', 'Aland Islands'), (b'AL', 'Albania'), (b'DZ', 'Algeria'), (b'AS', 'American Samoa'), (b'AD', 'Andorra'), (b'AO', 'Angola'), (b'AI', 'Anguilla'), (b'AQ', 'Antarctica'), (b'AG', 'Antigua and Barbuda'), (b'AR', 'Argentina'), (b'AM', 'Armenia'), (b'AW', 'Aruba'), (b'AU', 'Australia'), (b'AT', 'Austria'), (b'AZ', 'Azerbaijan'), (b'BS', 'Bahamas'), (b'BH', 'Bahrain'), (b'BD', 'Bangladesh'), (b'BB', 'Barbados'), (b'BY', 'Belarus'), (b'BE', 'Belgium'), (b'BZ', 'Belize'), (b'BJ', 'Benin'), (b'BM', 'Bermuda'), (b'BT', 'Bhutan'), (b'BO', 'Bolivia'), (b'BA', 'Bosnia and Herzegovina'), (b'BW', 'Botswana'), (b'BV', 'Bouvet Island'), (b'BR', 'Brazil'), (b'IO', 'British Indian Ocean Territory'), (b'BN', 'Brunei Darussalam'), (b'BG', 'Bulgaria'), (b'BF', 'Burkina Faso'), (b'BI', 'Burundi'), (b'KH', 'Cambodia'), (b'CM', 'Cameroon'), (b'CA', 'Canada'), (b'CV', 'Cape Verde'), (b'KY', 'Cayman Islands'), (b'CF', 'Central African Republic'), (b'TD', 'Chad'), (b'CL', 'Chile'), (b'CN', 'China'), (b'CX', 'Christmas Island'), (b'CC', 'Cocos (Keeling) Islands'), (b'CO', 'Colombia'), (b'KM', 'Comoros'), (b'CG', 'Congo'), (b'CD', 'Congo, The Democratic Republic of the'), (b'CK', 'Cook Islands'), (b'CR', 'Costa Rica'), (b'CI', "Cote d'Ivoire"), (b'HR', 'Croatia'), (b'CU', 'Cuba'), (b'CY', 'Cyprus'), (b'CZ', 'Czech Republic'), (b'DK', 'Denmark'), (b'DJ', 'Djibouti'), (b'DM', 'Dominica'), (b'DO', 'Dominican Republic'), (b'EC', 'Ecuador'), (b'EG', 'Egypt'), (b'SV', 'El Salvador'), (b'GQ', 'Equatorial Guinea'), (b'ER', 'Eritrea'), (b'EE', 'Estonia'), (b'ET', 'Ethiopia'), (b'FK', 'Falkland Islands (Malvinas)'), (b'FO', 'Faroe Islands'), (b'FJ', 'Fiji'), (b'FI', 'Finland'), (b'FR', 'France'), (b'GF', 'French Guiana'), (b'PF', 'French Polynesia'), (b'TF', 'French Southern Territories'), (b'GA', 'Gabon'), (b'GM', 'Gambia'), (b'GE', 'Georgia'), (b'DE', 'Germany'), (b'GH', 'Ghana'), (b'GI', 'Gibraltar'), (b'GR', 'Greece'), (b'GL', 'Greenland'), (b'GD', 'Grenada'), (b'GP', 'Guadeloupe'), (b'GU', 'Guam'), (b'GT', 'Guatemala'), (b'GG', 'Guernsey'), (b'GN', 'Guinea'), (b'GW', 'Guinea-Bissau'), (b'GY', 'Guyana'), (b'HT', 'Haiti'), (b'HM', 'Heard Island and McDonald Islands'), (b'VA', 'Holy See (Vatican City State)'), (b'HN', 'Honduras'), (b'HK', 'Hong Kong'), (b'HU', 'Hungary'), (b'IS', 'Iceland'), (b'IN', 'India'), (b'ID', 'Indonesia'), (b'IR', 'Iran, Islamic Republic of'), (b'IQ', 'Iraq'), (b'IE', 'Ireland'), (b'IM', 'Isle of Man'), (b'IL', 'Israel'), (b'IT', 'Italy'), (b'JM', 'Jamaica'), (b'JP', 'Japan'), (b'JE', 'Jersey'), (b'JO', 'Jordan'), (b'KZ', 'Kazakhstan'), (b'KE', 'Kenya'), (b'KI', 'Kiribati'), (b'KP', "Korea, Democratic People's Republic of"), (b'KR', 'Korea, Republic of'), (b'KW', 'Kuwait'), (b'KG', 'Kyrgyzstan'), (b'LA', "Lao People's Democratic Republic"), (b'LV', 'Latvia'), (b'LB', 'Lebanon'), (b'LS', 'Lesotho'), (b'LR', 'Liberia'), (b'LY', 'Libyan Arab Jamahiriya'), (b'LI', 'Liechtenstein'), (b'LT', 'Lithuania'), (b'LU', 'Luxembourg'), (b'MO', 'Macao'), (b'MK', 'Macedonia, The Former Yugoslav Republic of'), (b'MG', 'Madagascar'), (b'MW', 'Malawi'), (b'MY', 'Malaysia'), (b'MV', 'Maldives'), (b'ML', 'Mali'), (b'MT', 'Malta'), (b'MH', 'Marshall Islands'), (b'MQ', 'Martinique'), (b'MR', 'Mauritania'), (b'MU', 'Mauritius'), (b'YT', 'Mayotte'), (b'MX', 'Mexico'), (b'FM', 'Micronesia, Federated States of'), (b'MD', 'Moldova'), (b'MC', 'Monaco'), (b'MN', 'Mongolia'), (b'ME', 'Montenegro'), (b'MS', 'Montserrat'), (b'MA', 'Morocco'), (b'MZ', 'Mozambique'), (b'MM', 'Myanmar'), (b'NA', 'Namibia'), (b'NR', 'Nauru'), (b'NP', 'Nepal'), (b'NL', 'Netherlands'), (b'AN', 'Netherlands Antilles'), (b'NC', 'New Caledonia'), (b'NZ', 'New Zealand'), (b'NI', 'Nicaragua'), (b'NE', 'Niger'), (b'NG', 'Nigeria'), (b'NU', 'Niue'), (b'NF', 'Norfolk Island'), (b'MP', 'Northern Mariana Islands'), (b'NO', 'Norway'), (b'OM', 'Oman'), (b'PK', 'Pakistan'), (b'PW', 'Palau'), (b'PS', 'Palestinian Territory, Occupied'), (b'PA', 'Panama'), (b'PG', 'Papua New Guinea'), (b'PY', 'Paraguay'), (b'PE', 'Peru'), (b'PH', 'Philippines'), (b'PN', 'Pitcairn'), (b'PL', 'Poland'), (b'PT', 'Portugal'), (b'PR', 'Puerto Rico'), (b'QA', 'Qatar'), (b'RE', 'Reunion'), (b'RO', 'Romania'), (b'RU', 'Russian Federation'), (b'RW', 'Rwanda'), (b'BL', 'Saint Barthelemy'), (b'SH', 'Saint Helena'), (b'KN', 'Saint Kitts and Nevis'), (b'LC', 'Saint Lucia'), (b'MF', 'Saint Martin'), (b'PM', 'Saint Pierre and Miquelon'), (b'VC', 'Saint Vincent and the Grenadines'), (b'WS', 'Samoa'), (b'SM', 'San Marino'), (b'ST', 'Sao Tome and Principe'), (b'SA', 'Saudi Arabia'), (b'SN', 'Senegal'), (b'RS', 'Serbia'), (b'SC', 'Seychelles'), (b'SL', 'Sierra Leone'), (b'SG', 'Singapore'), (b'SK', 'Slovakia'), (b'SI', 'Slovenia'), (b'SB', 'Solomon Islands'), (b'SO', 'Somalia'), (b'ZA', 'South Africa'), (b'GS', 'South Georgia and the South Sandwich Islands'), (b'ES', 'Spain'), (b'LK', 'Sri Lanka'), (b'SD', 'Sudan'), (b'SR', 'Suriname'), (b'SJ', 'Svalbard and Jan Mayen'), (b'SZ', 'Swaziland'), (b'SE', 'Sweden'), (b'CH', 'Switzerland'), (b'SY', 'Syrian Arab Republic'), (b'TW', 'Taiwan, Province of China'), (b'TJ', 'Tajikistan'), (b'TZ', 'Tanzania, United Republic of'), (b'TH', 'Thailand'), (b'TL', 'Timor-Leste'), (b'TG', 'Togo'), (b'TK', 'Tokelau'), (b'TO', 'Tonga'), (b'TT', 'Trinidad and Tobago'), (b'TN', 'Tunisia'), (b'TR', 'Turkey'), (b'TM', 'Turkmenistan'), (b'TC', 'Turks and Caicos Islands'), (b'TV', 'Tuvalu'), (b'UG', 'Uganda'), (b'UA', 'Ukraine'), (b'AE', 'United Arab Emirates'), (b'GB', 'United Kingdom'), (b'US', 'United States'), (b'UM', 'United States Minor Outlying Islands'), (b'UY', 'Uruguay'), (b'UZ', 'Uzbekistan'), (b'VU', 'Vanuatu'), (b'VE', 'Venezuela'), (b'VN', 'Viet Nam'), (b'VG', 'Virgin Islands, British'), (b'VI', 'Virgin Islands, U.S.'), (b'WF', 'Wallis and Futuna'), (b'EH', 'Western Sahara'), (b'YE', 'Yemen'), (b'ZM', 'Zambia'), (b'ZW', 'Zimbabwe')])),
                ('type', models.CharField(max_length=20, verbose_name='type', choices=[(b'visiting', 'Visiting address'), (b'billing', 'Billing address'), (b'shipping', 'Shipping address'), (b'home', 'Home address'), (b'other', 'Other')])),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'address',
                'verbose_name_plural': 'addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_address', models.EmailField(max_length=255, verbose_name='e-mail address')),
                ('is_primary', models.BooleanField(default=False, verbose_name='primary e-mail')),
                ('status', models.IntegerField(default=1, max_length=50, verbose_name='status', choices=[(0, 'Inactive'), (1, 'Active')])),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'e-mail address',
                'verbose_name_plural': 'e-mail addresses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoryListItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_by_date', models.DateTimeField(verbose_name=b'date to sort by')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_utils.historylistitem_set', editable=False, to='contenttypes.ContentType', null=True)),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_input', models.CharField(max_length=40, verbose_name='phone number')),
                ('number', models.CharField(max_length=40)),
                ('type', models.CharField(default=b'work', max_length=15, verbose_name='type', choices=[(b'work', 'Work'), (b'mobile', 'Mobile'), (b'other', 'Other')])),
                ('other_type', models.CharField(max_length=15, null=True, blank=True)),
                ('status', models.IntegerField(default=1, max_length=10, verbose_name='status', choices=[(0, 'Inactive'), (1, 'Active')])),
                ('tenant', models.ForeignKey(to='tenant.Tenant', blank=True)),
            ],
            options={
                'verbose_name': 'phone number',
                'verbose_name_plural': 'phone numbers',
            },
            bases=(models.Model,),
        ),
    ]
