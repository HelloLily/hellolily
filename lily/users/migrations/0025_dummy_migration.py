from django.db import migrations, models


def dummy_forward(apps, schema_editor):
    pass

def dummy_backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_auto_20171221_1325'),
    ]

    operations = [
        migrations.RunPython(dummy_forward, dummy_backwards),
    ]