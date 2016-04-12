#################
Migrating in Lily
#################
We use the built-in Django migrations for both our schema & data migrations.
For more detailed information you should take a look at the `Django docs <https://docs.djangoproject.com/en/1.9/topics/migrations/>`_.

=======
Caveats
=======
Data migrations have two things you need to know about:
    - The modified date
    - Seperating schema and data changes

~~~~~~~~~~~~~
Modified date
~~~~~~~~~~~~~
It is important to disable the updating of modified fields on models during data migrations.
The modified date should always represent the date a **user** last modified it.

Unfortunately as of writing, there is no way to set this behaviour automatically, so you'll have to do it yourself using `update_modified = False`.

Practical example:

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals

    from django.db import models, migrations


    def data_migration_forward(apps, schema_editor):
        Account = apps.get_model('accounts', 'Account')

        for account in Account.objects.all():
            account.update_modified = False
            # Do some mutations on the account here
            account.save()  # Because update_modified is False, this will not update the modified date of the account.

    class Migration(migrations.Migration):
        dependencies = []

        operations = [
            migrations.RunPython(data_migration_forward),
        ]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Seperation of schema/data changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You should **never** combine a schema and data migration in a single migration file.
This is because of consistency and error prevention.
In some cases it is possible to combine the two, but you still shouldn't do it.

.. code-block:: none

    Thus, on PostgreSQL, for example, you should avoid combining schema changes and RunPython operations
    in the same migration or you may hit errors like OperationalError: cannot ALTER TABLE "mytable"
    because it has pending trigger events.

As can be read on the `Django docs <https://docs.djangoproject.com/en/1.9/ref/migration-operations/#runpython>`_ somewhat near the end of the block.


<input value='asfdsdf' />
