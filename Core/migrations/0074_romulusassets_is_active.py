# Generated by Django 4.2.3 on 2023-08-02 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0073_alter_totalizerreadings_left_reading'),
    ]

    operations = [
        migrations.AddField(
            model_name='romulusassets',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
