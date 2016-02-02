# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('deals', '0018_auto_20160203_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='account',
            field=models.ForeignKey(verbose_name='account', to='accounts.Account'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_once',
            field=models.DecimalField(verbose_name='one-time cost', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='amount_recurring',
            field=models.DecimalField(verbose_name='recurring costs', max_digits=19, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='contacted_by',
            field=models.IntegerField(max_length=255, verbose_name='contacted us by',
                                      choices=[(0, 'Quote'), (1, 'Contact form'), (2, 'Phone'), (3, 'Web chat'),
                                               (4, 'E-mail'), (6, 'Instant connect'), (5, 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='currency',
            field=models.CharField(max_length=3, verbose_name='currency',
                                   choices=[(b'EUR', 'Euro'), (b'GBP', 'British pound'), (b'NOR', 'Norwegian krone'),
                                            (b'DKK', 'Danish krone'), (b'SEK', 'Swedish krone'),
                                            (b'CHF', 'Swiss franc'), (b'USD', 'United States dollar')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='found_through',
            field=models.IntegerField(max_length=255, verbose_name='found us through',
                                      choices=[(0, 'Search engine'), (1, 'Social media'), (2, 'Talk with employee'),
                                               (3, 'Existing customer'), (5, 'Radio'), (6, 'Public speaking'),
                                               (7, 'Press and articles'), (4, 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='next_step',
            field=models.ForeignKey(related_name='deals', verbose_name='next step', to='deals.DealNextStep'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='stage',
            field=models.IntegerField(verbose_name='status',
                                      choices=[(0, 'Open'), (1, 'Proposal sent'), (2, 'Won'), (3, 'Lost'),
                                               (4, 'Called'), (5, 'Emailed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='deal',
            name='why_customer',
            field=models.ForeignKey(related_name='deals', verbose_name='why', to='deals.DealWhyCustomer'),
            preserve_default=True,
        ),
    ]

