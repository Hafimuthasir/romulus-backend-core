# Generated by Django 4.2.3 on 2023-07-20 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0027_romulusassets_capacity_romulusassets_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='romulusassets',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
