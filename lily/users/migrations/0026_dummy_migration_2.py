from django.db import migrations, models


def dummy_forward(apps, schema_editor):
    raise ValueError("Migration failed because I want to test migration failures.")

def dummy_backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_dummy_migration'),
    ]

    operations = [
        migrations.RunPython(dummy_forward, dummy_backwards),
    ]