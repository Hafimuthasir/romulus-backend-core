# Generated by Django 4.2.1 on 2023-05-28 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_alter_assets_assetregistrationnumber'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assets',
            name='fuelType',
            field=models.CharField(default=True, max_length=255),
        ),
    ]
