# Generated by Django 4.2.1 on 2023-05-24 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0005_remove_assets_assetincharge_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assets',
            name='assetRegistrationNumber',
            field=models.CharField(blank=True, default=11, max_length=255),
            preserve_default=False,
        ),
    ]